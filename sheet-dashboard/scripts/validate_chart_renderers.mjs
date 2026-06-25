#!/usr/bin/env node

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel'
const SUPPORTED_LIBRARIES = new Set(['echarts', 'highcharts', 'shadcn'])

function usage() {
  console.error(`Usage:
  node scripts/validate_chart_renderers.mjs --uri <sheet_uri> --worksheet <worksheet_name> [options]

Options:
  --chart-id <id>       Validate only one chart. Repeatable.
  --no-formula-check    Skip SQL dataframe fetch and only parse renderer objects.
`)
}

function parseArgs(argv) {
  const args = {
    chartIds: [],
    formulaCheck: true,
  }

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index]
    switch (token) {
      case '--uri':
        args.uri = argv[index + 1]
        index += 1
        break
      case '--worksheet':
        args.worksheet = argv[index + 1]
        index += 1
        break
      case '--chart-id':
        args.chartIds.push(argv[index + 1])
        index += 1
        break
      case '--no-formula-check':
        args.formulaCheck = false
        break
      case '--help':
      case '-h':
        usage()
        process.exit(0)
      default:
        throw new Error(`Unknown argument: ${token}`)
    }
  }

  if (!args.uri || !args.worksheet) {
    usage()
    throw new Error('--uri and --worksheet are required')
  }

  return args
}

function getToken() {
  const token = String(process.env.MAYBEAI_API_TOKEN || '').trim()
  if (!token) throw new Error('MAYBEAI_API_TOKEN is not set')
  return token
}

async function post(path, payload) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new Error(`${path} failed: ${response.status} ${response.statusText} ${body}`)
  }

  const data = await response.json()
  if (data && data.success === false) {
    throw new Error(`${path} failed: ${JSON.stringify(data)}`)
  }
  return data
}

function normalizeSql(sql) {
  return String(sql || '').replace(/\s+/g, ' ').trim().replace(/;$/, '')
}

function buildSqlFormula(sql) {
  const trimmed = normalizeSql(sql)
  return `=SQL("${trimmed.replace(/"/g, '""')}")`
}

function tableToRows(values) {
  if (!Array.isArray(values) || values.length === 0) return []
  const headers = (values[0] || []).map((value) => String(value ?? ''))
  return values.slice(1).map((row) =>
    Object.fromEntries(headers.map((header, index) => [header, row?.[index]])),
  )
}

function parseObjectLiteral(source) {
  return new Function('"use strict"; return (' + String(source || '') + ');')()
}

async function fetchSqlRows(uri, sql) {
  const data = await post('/calc_formulas', {
    uri,
    formulas: [
      {
        cell: 'A1',
        formula: buildSqlFormula(sql),
      },
    ],
  })
  const result = Array.isArray(data.results) ? data.results[0] : null
  if (result?.error) throw new Error(result.error)
  return tableToRows(result?.range_values || [])
}

function inspectRendererShape(chart, renderer) {
  const errors = []
  const warnings = []
  const library = String(renderer?.library || '')

  if (!library) errors.push('missing renderer library')
  else if (!SUPPORTED_LIBRARIES.has(library)) errors.push(`unsupported renderer library: ${library}`)

  if (library === 'shadcn') {
    if (!renderer.component) errors.push('shadcn renderer missing component')
    return { library, errors, warnings }
  }

  if (library === 'echarts' || library === 'highcharts') {
    if (typeof renderer.handler !== 'function') {
      errors.push(`${library} renderer.handler is not a function`)
    }
  }

  const html = String(chart.html || '')
  if (chart.type === 'json' && /<html|<script|document\.|window\./i.test(html)) {
    errors.push('json chart.html contains full HTML/browser globals instead of a renderer object')
  }
  if (html.includes('font:')) {
    warnings.push('uses ECharts graphic style.font shorthand; prefer fontFamily/fontSize/fontWeight')
  }
  if (/title\s*:\s*\{[^}]*text\s*:/.test(html) && chart.title && chart.spec?.style?.showContainerTitle !== false) {
    warnings.push('possible duplicate visible title; preserve chart.title and set spec.style.showContainerTitle=false')
  }

  return { library, errors, warnings }
}

function chartPixelSize(chart) {
  return {
    width: Number(chart.width || chart.dimension?.width || 0),
    height: Number(chart.height || chart.dimension?.height || 0),
  }
}

function inspectRendererInternalDimensions(chart) {
  const errors = []
  const warnings = []
  const { width, height } = chartPixelSize(chart)
  if (!width || !height) return { errors, warnings }

  const html = String(chart.html || '')
  const constWH = [...html.matchAll(/const\s+W\s*=\s*(\d+)\s*,\s*H\s*=\s*(\d+)/g)].map(
    (match) => [Number(match[1]), Number(match[2])],
  )
  const constW = [...html.matchAll(/const\s+W\s*=\s*(\d+)\s*(?:;|,)/g)].map((match) =>
    Number(match[1]),
  )
  const shapeWH = [...html.matchAll(/shape:\{width:(\d+),height:(\d+)/g)].map((match) => [
    Number(match[1]),
    Number(match[2]),
  ])

  const driftedConst = constWH.filter(
    ([innerWidth, innerHeight]) => Math.abs(innerWidth - width) > 2 || Math.abs(innerHeight - height) > 2,
  )
  const driftedConstW = constW.filter((innerWidth) => Math.abs(innerWidth - width) > 2)

  if (driftedConst.length) {
    errors.push(
      `renderer internal const W/H ${driftedConst
        .map(([innerWidth, innerHeight]) => `${innerWidth}x${innerHeight}`)
        .join(', ')} does not match chart size ${width}x${height}`,
    )
  } else if (driftedConstW.length) {
    errors.push(
      `renderer internal const W ${driftedConstW.join(', ')} does not match chart width ${width}`,
    )
  }

  const maxShape = shapeWH
    .filter(([innerWidth, innerHeight]) => innerWidth >= 300 && innerHeight >= 80)
    .sort((left, right) => right[0] * right[1] - left[0] * left[1])[0]
  if (maxShape) {
    const [shapeWidth, shapeHeight] = maxShape
    const largeDrift =
      Math.abs(shapeWidth - width) > 2 &&
      (shapeWidth > width * 1.05 ||
        width > shapeWidth * 1.25 ||
        shapeHeight > height * 1.05 ||
        height > shapeHeight * 1.25)
    if (largeDrift) {
      errors.push(
        `largest graphic rect ${shapeWidth}x${shapeHeight} does not match chart size ${width}x${height}; graphic surfaces may only fill part of the chart`,
      )
    }
  }

  const driftedBars = shapeWH.filter(
    ([innerWidth, innerHeight]) =>
      innerHeight >= 24 && innerHeight <= 60 && innerWidth >= 300 && Math.abs(innerWidth - width) > 2,
  )
  if (driftedBars.length) {
    errors.push(
      `graphic header/section bar width ${driftedBars
        .map(([innerWidth, innerHeight]) => `${innerWidth}x${innerHeight}`)
        .join(', ')} does not match chart width ${width}`,
    )
  }

  return { errors, warnings }
}

function inspectGraphicAlignmentContract(chart) {
  const errors = []
  const warnings = []
  const html = String(chart.html || '')
  const spec = chart?.spec && typeof chart.spec === 'object' ? chart.spec : {}
  const style = spec.style && typeof spec.style === 'object' ? spec.style : {}
  const layout = spec.layout && typeof spec.layout === 'object' ? spec.layout : {}
  const slotId = String(style.slot_id || style.slotId || '')
  const titleText = String(chart.title || '')
  const isTitleHeader =
    /(?:^|_)(?:title|header|hero|report)(?:_|$)/i.test(slotId) ||
    /标题|表头|报告|驾驶舱|总览|概览/.test(titleText)
  const isKpiLike =
    /kpi|gauge|conversion|target|callout|summary|stat/i.test(slotId) ||
    /KPI|指标|仪表|转化|核心|数字|达成/.test(titleText)

  const hasPrimaryKpiLeftAnchor =
    /left:\s*x\s*\+\s*1[02468][^}\n]{0,220}align:\s*['"]left['"]/i.test(html) ||
    /left:\s*x\s*\+\s*14[^}\n]{0,220}text:\s*(?:money\(m\[1\]\)|m\[0\])[^}\n]{0,220}align:\s*['"]left['"]/i.test(html)

  if (isKpiLike && hasPrimaryKpiLeftAnchor) {
    errors.push(
      'primary KPI label/value uses a left-padding anchor; use card/gauge center with align:center and verticalAlign:middle',
    )
  }

  const kpiValueCentered = layout.kpi_value_centered === true || style.kpi_value_centered === true
  if (isKpiLike && kpiValueCentered) {
    const hasCenterAnchor = /left:\s*(?:x\s*\+\s*cw\s*\/\s*2|W\s*\/\s*2|['"]center['"])/.test(html)
    const hasMiddleAlign = /verticalAlign:\s*['"]middle['"]/.test(html)
    if (!hasCenterAnchor || !hasMiddleAlign) {
      errors.push(
        'spec.layout.kpi_value_centered=true but renderer does not expose center anchors with verticalAlign:middle',
      )
    }
  } else if (isKpiLike && !/series:\s*\[\s*\{[^}]*type:\s*['"]gauge['"]/s.test(html)) {
    warnings.push('KPI-like chart does not declare spec.layout.kpi_value_centered=true')
  }

  if (isTitleHeader) {
    const titleAlignment = String(layout.title_alignment || style.title_alignment || '')
    const expectsCenteredTitle =
      layout.title_centered_in_background === true ||
      style.title_centered_in_background === true ||
      titleAlignment === 'center_in_background'
    const expectsIdentityLeft =
      titleAlignment === 'identity_left' ||
      layout.main_title_from_data_and_sheet_title === true ||
      style.main_title_from_data_and_sheet_title === true
    const hasCenteredText = /align:\s*['"]center['"][^}\n]{0,180}verticalAlign:\s*['"]middle['"]/.test(html)
    const hasLeftIdentityText = /align:\s*['"]left['"][^}\n]{0,180}verticalAlign:\s*['"]middle['"]/.test(html)
    const hasMiddleAlign = /verticalAlign:\s*['"]middle['"]/.test(html)
    const hasMainTitleSource =
      layout.main_title_from_data_and_sheet_title === true ||
      /mainTitle\s*=\s*company\s*\+|actualCompany|spreadsheet_title|workbook title/i.test(html)

    if (expectsCenteredTitle && !hasCenteredText) {
      errors.push(
        'spec.layout.title_centered_in_background=true but renderer lacks centered text with verticalAlign:middle',
      )
    }
    if (expectsIdentityLeft && (!hasLeftIdentityText || !hasMiddleAlign)) {
      errors.push(
        'identity title/header should use left-aligned text with verticalAlign:middle inside its background',
      )
    }
    if (!hasMainTitleSource) {
      warnings.push(
        'title/header chart does not prove its main title comes from workbook/company/report identity',
      )
    }
    if (
      !expectsCenteredTitle &&
      !expectsIdentityLeft &&
      !layout.title_inside_background &&
      !style.title_inside_background
    ) {
      warnings.push('title/header chart does not declare title alignment or title_inside_background metadata')
    }
  }

  return { errors, warnings }
}

function inspectStyleMetadata(chart) {
  const style = chart?.spec?.style && typeof chart.spec.style === 'object' ? chart.spec.style : {}
  const warnings = []

  const hasPack =
    chart.dashboard_style_pack_id ||
    style.dashboard_style_pack_id ||
    style.dashboardStylePackId ||
    style.dashboard_style_pack?.id
  const hasStyleSource = chart.style_source || style.style_source || style.styleSource
  const hasIndustry = chart.industry || style.industry || style.industry_style || style.industryStyle
  const hasVariant = chart.style_variant || style.style_variant || style.variant

  if (!hasPack) warnings.push('missing dashboard_style_pack_id metadata')
  if (!hasStyleSource) warnings.push('missing style_source metadata')
  if (!hasIndustry) warnings.push('missing industry metadata')
  if (!hasVariant) warnings.push('missing style_variant metadata')

  return warnings
}

function inspectChartOption(option) {
  const errors = []
  const warnings = []

  if (!option || typeof option !== 'object') {
    errors.push('handler returned non-object')
    return { errors, warnings }
  }

  if (!option.series && !option.graphic) {
    warnings.push('option has neither series nor graphic')
  }
  if (option.series && !Array.isArray(option.series)) {
    errors.push('option.series is not an array')
  }
  if (Array.isArray(option.series)) {
    option.series.forEach((series, index) => {
      if (!series || typeof series !== 'object') {
        errors.push(`series[${index}] is not an object`)
        return
      }
      if (!series.type) warnings.push(`series[${index}] missing type`)
      if (!Array.isArray(series.data)) warnings.push(`series[${index}] missing data array`)
      if (Array.isArray(series.data) && series.data.some((value) => Number.isNaN(value))) {
        warnings.push(`series[${index}] contains NaN`)
      }
    })
  }

  const xAxis = Array.isArray(option.xAxis) ? option.xAxis[0] : option.xAxis
  if (xAxis?.data && Array.isArray(option.series)) {
    option.series.forEach((series, index) => {
      if (Array.isArray(series.data) && series.data.length !== xAxis.data.length) {
        warnings.push(`series[${index}] data length ${series.data.length} differs from xAxis ${xAxis.data.length}`)
      }
    })
  }

  return { errors, warnings }
}

async function validateChart(args, chart) {
  const result = {
    chart_id: chart.chart_id,
    title: chart.title,
    type: chart.type,
    library: '',
    rows: null,
    errors: [],
    warnings: [],
  }

  if (chart.type !== 'json') {
    result.warnings.push(`chart.type is ${chart.type || '<empty>'}; renderer validation is optimized for json charts`)
  }

  let renderer
  try {
    renderer = parseObjectLiteral(chart.html)
  } catch (error) {
    result.errors.push(`chart.html parse failed: ${error.message}`)
    return result
  }

  const shape = inspectRendererShape(chart, renderer)
  result.library = shape.library
  result.errors.push(...shape.errors)
  result.warnings.push(...shape.warnings)
  const internalDimensions = inspectRendererInternalDimensions(chart)
  result.errors.push(...internalDimensions.errors)
  result.warnings.push(...internalDimensions.warnings)
  const alignmentContract = inspectGraphicAlignmentContract(chart)
  result.errors.push(...alignmentContract.errors)
  result.warnings.push(...alignmentContract.warnings)
  result.warnings.push(...inspectStyleMetadata(chart))
  if (result.errors.length > 0) return result

  if (!args.formulaCheck) return result

  let rows = []
  try {
    rows = await fetchSqlRows(args.uri, chart.sql)
    result.rows = rows.length
  } catch (error) {
    result.errors.push(`SQL dataframe fetch failed: ${error.message}`)
    return result
  }

  if (result.library === 'shadcn') return result

  try {
    const option = renderer.handler(rows)
    const inspected = inspectChartOption(option)
    result.errors.push(...inspected.errors)
    result.warnings.push(...inspected.warnings)
  } catch (error) {
    result.errors.push(`renderer.handler failed: ${error.message}`)
  }

  return result
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const chartsResponse = await post('/get_charts', {
    uri: args.uri,
    worksheet_name: args.worksheet,
  })
  let charts = Array.isArray(chartsResponse.charts) ? chartsResponse.charts : []
  if (args.chartIds.length) {
    const wanted = new Set(args.chartIds)
    charts = charts.filter((chart) => wanted.has(chart.chart_id))
  }

  const results = []
  for (const chart of charts) {
    results.push(await validateChart(args, chart))
  }

  for (const result of results) {
    console.log(`[chart] ${result.chart_id} ${result.title || ''}`)
    console.log(`  library: ${result.library || '<unknown>'} rows: ${result.rows ?? '<skipped>'}`)
    for (const error of result.errors) console.log(`  ERROR: ${error}`)
    for (const warning of result.warnings) console.log(`  WARN: ${warning}`)
  }

  const errorCount = results.reduce((sum, result) => sum + result.errors.length, 0)
  const warningCount = results.reduce((sum, result) => sum + result.warnings.length, 0)
  console.log('\n[summary]')
  console.log(`  charts scanned: ${results.length}`)
  console.log(`  errors: ${errorCount}`)
  console.log(`  warnings: ${warningCount}`)

  if (errorCount > 0) process.exitCode = 1
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
