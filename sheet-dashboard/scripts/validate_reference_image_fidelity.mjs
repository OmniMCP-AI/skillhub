#!/usr/bin/env node

import fs from 'node:fs'

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel'
const CELL_WIDTH_PX = 101
const CELL_HEIGHT_PX = 27

const IMAGE_DERIVED_PACKS = {
  'financial-teal-executive-summary-report': {
    requiredBackground: '#EEF6F6',
    visualSkeleton: {
      sectionBar: '#66A9AA',
      moduleSurface: '#F8FCFC',
      border: '#CADCDD',
      tableHeaderFill: '#E6EFEF',
      tableHeaderText: '#2F343A',
    },
    similarityAcceptance: {
      minGraphicCardRatio: 0.85,
      maxPlainAxisModules: 1,
      requiredSectionBarRatio: 0.75,
      requiredSlotMatchRatio: 0.8,
    },
    densityAcceptance: {
      maxUniformInsetCharts: 6,
      minAverageHtmlLength: 1600,
    },
    slots: [
      {
        slotId: 'executive_title',
        role: 'text_header',
        from: 'B2',
        to: 'N7',
        archetype: 'graphic_identity_strip',
        toleranceRows: 2,
        requiredFeatures: ['graphic_rect_surface', 'large_report_title', 'identity_fallback_text'],
        density: { minTextElements: 5, minRectElements: 4, minHtmlLength: 1400 },
      },
      {
        slotId: 'company_profile',
        role: 'table',
        from: 'B9',
        to: 'G17',
        archetype: 'graphic_report_table',
        toleranceRows: 3,
        requiresRightPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'light_header_fill', 'bounded_text_columns'],
        density: { minTextElements: 4, minRectElements: 4, minHtmlLength: 1800, minTableRows: 4 },
      },
      {
        slotId: 'product_summary',
        role: 'table',
        from: 'H9',
        to: 'N17',
        archetype: 'graphic_report_table',
        toleranceRows: 3,
        requiresLeftPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'light_header_fill', 'bounded_text_columns'],
        density: { minTextElements: 4, minRectElements: 4, minHtmlLength: 1800, minTableRows: 4 },
      },
      {
        slotId: 'financial_summary_kpis',
        role: 'kpi',
        from: 'B19',
        to: 'N25',
        archetype: 'graphic_kpi_card_strip',
        toleranceRows: 3,
        requiredFeatures: ['graphic_rect_surface', 'outlined_kpi_cards', 'centered_values'],
        density: { minTextElements: 5, minRectElements: 4, minHtmlLength: 2200, minCards: 4 },
      },
      {
        slotId: 'segment_revenue',
        role: 'table',
        from: 'B27',
        to: 'G37',
        archetype: 'graphic_report_table',
        toleranceRows: 4,
        requiresRightPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'light_header_fill', 'bounded_text_columns'],
        density: { minTextElements: 3, minRectElements: 2, minHtmlLength: 1400, minTableRows: 3 },
      },
      {
        slotId: 'key_metrics',
        role: 'table',
        from: 'H27',
        to: 'N37',
        archetype: 'graphic_report_table',
        toleranceRows: 4,
        requiresLeftPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'light_header_fill', 'bounded_text_columns'],
        density: { minTextElements: 3, minRectElements: 2, minHtmlLength: 1400, minTableRows: 3 },
      },
      {
        slotId: 'segment_change_table',
        role: 'table',
        from: 'B39',
        to: 'G49',
        archetype: 'graphic_report_table',
        toleranceRows: 4,
        requiresRightPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'light_header_fill', 'bounded_text_columns'],
        density: { minTextElements: 4, minRectElements: 4, minHtmlLength: 1800, minTableRows: 4 },
      },
      {
        slotId: 'revenue_mix',
        role: 'composition',
        from: 'H39',
        to: 'N49',
        archetype: 'graphic_donut_composition',
        toleranceRows: 4,
        requiresLeftPadding: true,
        requiredFeatures: ['graphic_rect_surface', 'section_bar', 'donut_with_side_labels'],
        density: { minTextElements: 5, minRectElements: 2, minHtmlLength: 1700, minLegendItems: 3 },
      },
      {
        slotId: 'financial_highlights',
        role: 'kpi_tile_grid',
        from: 'B51',
        to: 'N61',
        archetype: 'graphic_kpi_tile_grid',
        toleranceRows: 5,
        requiredFeatures: ['graphic_rect_surface', 'outlined_tiles'],
        density: { minTextElements: 5, minRectElements: 4, minHtmlLength: 1600, minTiles: 4 },
      },
    ],
  },
}

function usage() {
  console.error(`Usage:
  node scripts/validate_reference_image_fidelity.mjs --uri <sheet_uri> --worksheet <worksheet_name> [options]
  node scripts/validate_reference_image_fidelity.mjs --charts-json <get_charts.json> [options]

Options:
  --expected-pack <id>       Validate against this image-derived pack.
  --charts-json <path>       Read a saved get_charts response instead of calling the API.
  --strict-density           Also validate report-card information density and area usage.
`)
}

function parseArgs(argv) {
  const args = {}

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
      case '--expected-pack':
        args.expectedPack = argv[index + 1]
        index += 1
        break
      case '--charts-json':
        args.chartsJson = argv[index + 1]
        index += 1
        break
      case '--strict-density':
        args.strictDensity = true
        break
      case '--help':
      case '-h':
        usage()
        process.exit(0)
        break
      default:
        throw new Error(`Unknown argument: ${token}`)
    }
  }

  if (!args.chartsJson && (!args.uri || !args.worksheet)) {
    usage()
    throw new Error('Either --charts-json or both --uri and --worksheet are required')
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

function normalizeValue(value) {
  return String(value ?? '').trim()
}

function toFiniteNumber(value) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

function columnLabelToIndex(label) {
  let col = 0
  for (const char of String(label || '').toUpperCase()) {
    if (char < 'A' || char > 'Z') return null
    col = col * 26 + (char.charCodeAt(0) - 64)
  }
  return col > 0 ? col - 1 : null
}

function parseCell(cell) {
  const match = normalizeValue(cell).match(/^([A-Za-z]+)(\d+)$/)
  if (!match) return null
  const col = columnLabelToIndex(match[1])
  const row = Number(match[2])
  if (col == null || !Number.isFinite(row) || row < 1) return null
  return { col, row: row - 1 }
}

function columnIndexToLabel(index) {
  let value = index + 1
  let label = ''
  while (value > 0) {
    const remainder = (value - 1) % 26
    label = String.fromCharCode(65 + remainder) + label
    value = Math.floor((value - 1) / 26)
  }
  return label
}

function toA1(col, row) {
  return `${columnIndexToLabel(col)}${row + 1}`
}

function parseRange(fromCell, toCell) {
  const from = parseCell(fromCell)
  const to = parseCell(toCell)
  if (!from || !to) throw new Error(`Invalid slot range ${fromCell}:${toCell}`)
  return {
    fromCol: from.col,
    fromRow: from.row,
    toCol: to.col + 1,
    toRow: to.row + 1,
  }
}

function rectLabel(rect) {
  return `${toA1(rect.fromCol, rect.fromRow)}:${toA1(rect.toCol - 1, rect.toRow - 1)}`
}

function getChartRect(chart) {
  const format = chart?.format || {}
  const fromCol = toFiniteNumber(format?.from?.col)
  const fromRow = toFiniteNumber(format?.from?.row)
  const toCol = toFiniteNumber(format?.to?.col)
  const toRow = toFiniteNumber(format?.to?.row)

  if (
    fromCol != null &&
    fromRow != null &&
    toCol != null &&
    toRow != null &&
    toCol > fromCol &&
    toRow > fromRow
  ) {
    return { fromCol, fromRow, toCol, toRow }
  }

  const anchor = parseCell(chart?.cell)
  if (!anchor) return null
  const width = toFiniteNumber(chart?.dimension?.width) ?? toFiniteNumber(chart?.width) ?? 13 * CELL_WIDTH_PX
  const height = toFiniteNumber(chart?.dimension?.height) ?? toFiniteNumber(chart?.height) ?? 10 * CELL_HEIGHT_PX
  return {
    fromCol: anchor.col,
    fromRow: anchor.row,
    toCol: anchor.col + Math.max(1, Math.round(width / CELL_WIDTH_PX)),
    toRow: anchor.row + Math.max(1, Math.round(height / CELL_HEIGHT_PX)),
  }
}

function getPackId(chart) {
  const style = chart?.spec?.style || {}
  const direct =
    chart.dashboard_style_pack_id ||
    style.dashboard_style_pack_id ||
    style.dashboardStylePackId ||
    style.dashboard_style_pack?.id
  if (direct) return String(direct)

  const source = String(chart.style_source || style.style_source || style.styleSource || '')
  for (const packId of Object.keys(IMAGE_DERIVED_PACKS)) {
    if (source.includes(packId)) return packId
  }
  return ''
}

function distance(rect, slot) {
  return (
    Math.abs(rect.fromCol - slot.fromCol) +
    Math.abs(rect.toCol - slot.toCol) +
    Math.abs(rect.fromRow - slot.fromRow) +
    Math.abs(rect.toRow - slot.toRow)
  )
}

function chartFitsSlot(rect, slot, toleranceRows) {
  return (
    Math.abs(rect.fromCol - slot.fromCol) <= 1 &&
    Math.abs(rect.toCol - slot.toCol) <= 1 &&
    Math.abs(rect.fromRow - slot.fromRow) <= toleranceRows &&
    Math.abs(rect.toRow - slot.toRow) <= toleranceRows
  )
}

function normalizeHtml(chart) {
  return String(chart?.html || '')
}

function hasGraphic(chart) {
  return /graphic\s*:/.test(normalizeHtml(chart))
}

function hasRect(chart) {
  return /type\s*:\s*['"]rect['"]/.test(normalizeHtml(chart))
}

function hasText(chart) {
  return /type\s*:\s*['"]text['"]/.test(normalizeHtml(chart)) || /style\s*:\s*\{[^}]*text\s*:/.test(normalizeHtml(chart))
}

function hasPieSeries(chart) {
  return /type\s*:\s*['"]pie['"]/.test(normalizeHtml(chart))
}

function hasPlainAxisRenderer(chart) {
  const html = normalizeHtml(chart)
  return /series\s*:/.test(html) && /xAxis\s*:/.test(html) && /yAxis\s*:/.test(html) && !(hasGraphic(chart) && hasRect(chart))
}

function hasSectionBar(chart, pack) {
  const html = normalizeHtml(chart).toUpperCase()
  const colors = [
    pack.visualSkeleton.sectionBar,
    '#4F989B',
    '#8FC4C5',
  ].filter(Boolean)
  return colors.some((color) => html.includes(color.toUpperCase())) && hasRect(chart)
}

function hasLightHeaderFill(chart, pack) {
  const html = normalizeHtml(chart).toUpperCase()
  const colors = [
    pack.visualSkeleton.tableHeaderFill,
    '#F2F2F2',
    '#EEF6F6',
    '#E6EFEF',
  ].filter(Boolean)
  return colors.some((color) => html.includes(color.toUpperCase()))
}

function hasBoundedText(chart) {
  const html = normalizeHtml(chart)
  return /width\s*:/.test(html) || /overflow\s*:\s*['"]truncate['"]/.test(html) || /ellipsis\s*:/.test(html)
}

function hasCenteredValues(chart) {
  const html = normalizeHtml(chart)
  return /align\s*:\s*['"]center['"]/.test(html) || /left\s*:\s*['"]center['"]/.test(html)
}

function countMatches(pattern, source) {
  const matches = String(source || '').match(pattern)
  return matches ? matches.length : 0
}

function inspectDensity(chart) {
  const html = normalizeHtml(chart)
  return {
    htmlLength: html.length,
    rectElements: countMatches(/type\s*:\s*['"]rect['"]/g, html),
    textElements:
      countMatches(/type\s*:\s*['"]text['"]/g, html) +
      countMatches(/style\s*:\s*\{[^}]*text\s*:/g, html),
    pieSeries: countMatches(/type\s*:\s*['"]pie['"]/g, html),
    widthRules: countMatches(/width\s*:/g, html),
    percentLabels: countMatches(/%/g, html),
    valueHints: countMatches(/value|amount|revenue|profit|cash|margin|成本|收入|利润|现金|指标|风险|建议|回款|用户/gi, html),
  }
}

function validateDensity(chart, slotSpec) {
  const required = slotSpec.density || {}
  const actual = inspectDensity(chart)
  const errors = []

  if (required.minHtmlLength && actual.htmlLength < required.minHtmlLength) {
    errors.push(`html length ${actual.htmlLength} below density minimum ${required.minHtmlLength}`)
  }
  if (required.minRectElements && actual.rectElements < required.minRectElements) {
    errors.push(`rect elements ${actual.rectElements} below density minimum ${required.minRectElements}`)
  }
  if (required.minTextElements && actual.textElements < required.minTextElements) {
    errors.push(`text elements ${actual.textElements} below density minimum ${required.minTextElements}`)
  }
  if (required.minTableRows && actual.textElements < required.minTableRows + 1) {
    errors.push(`table text elements ${actual.textElements} below table row density minimum ${required.minTableRows + 1}`)
  }
  if (required.minCards && actual.rectElements < required.minCards) {
    errors.push(`card surfaces ${actual.rectElements} below KPI card minimum ${required.minCards}`)
  }
  if (required.minLegendItems && actual.textElements < required.minLegendItems + 2) {
    errors.push(`legend/side-label text elements ${actual.textElements} below composition density minimum ${required.minLegendItems + 2}`)
  }
  if (required.minTiles && actual.rectElements < required.minTiles) {
    errors.push(`tile surfaces ${actual.rectElements} below tile minimum ${required.minTiles}`)
  }

  return { actual, errors }
}

function detectFeatures(chart, pack) {
  const features = new Set()
  if (hasGraphic(chart) && hasRect(chart)) features.add('graphic_rect_surface')
  if (hasSectionBar(chart, pack)) features.add('section_bar')
  if (hasLightHeaderFill(chart, pack)) features.add('light_header_fill')
  if (hasBoundedText(chart)) features.add('bounded_text_columns')
  if (/row_divider|divider|line|#DDEAEA|#CADCDD/i.test(normalizeHtml(chart))) features.add('row_dividers')
  if (hasCenteredValues(chart)) features.add('centered_values')
  if (/tile|card|outline|border|#CADCDD/i.test(normalizeHtml(chart)) && hasRect(chart)) features.add('outlined_tiles')
  if (/kpi|delta|percent|%/i.test(normalizeHtml(chart)) && hasRect(chart)) features.add('outlined_kpi_cards')
  if (hasPieSeries(chart)) features.add('donut_with_side_labels')
  if (/logo|identity|company|title|report/i.test(normalizeHtml(chart))) features.add('identity_fallback_text')
  if (hasText(chart)) features.add('large_report_title')
  return features
}

function archetypeSatisfied(chart, slotSpec, pack) {
  const features = detectFeatures(chart, pack)
  const missingFeatures = (slotSpec.requiredFeatures || []).filter((feature) => !features.has(feature))
  const html = normalizeHtml(chart)
  const failures = []

  switch (slotSpec.archetype) {
    case 'graphic_identity_strip':
      if (!hasGraphic(chart) || !hasRect(chart) || !hasText(chart)) {
        failures.push('identity strip must use ECharts graphic rect/text elements')
      }
      break
    case 'graphic_report_table':
      if (!hasGraphic(chart) || !hasRect(chart) || !hasText(chart)) {
        failures.push('report table must use ECharts graphic rect/text elements')
      }
      if (hasPlainAxisRenderer(chart)) failures.push('report table slot used a plain axis chart')
      break
    case 'graphic_kpi_card_strip':
    case 'graphic_kpi_tile_grid':
      if (!hasGraphic(chart) || !hasRect(chart) || !hasText(chart)) {
        failures.push(`${slotSpec.archetype} must use ECharts graphic rect/text elements`)
      }
      if (hasPlainAxisRenderer(chart)) failures.push(`${slotSpec.archetype} slot used a plain axis chart`)
      break
    case 'graphic_donut_composition':
      if (!hasGraphic(chart) || !hasRect(chart)) {
        failures.push('donut composition must keep a graphic report-card surface')
      }
      if (!hasPieSeries(chart) && !/donut|pie|composition|mix/i.test(html)) {
        failures.push('donut composition slot does not expose a donut/pie composition renderer')
      }
      break
    case 'axis_chart':
      if (!/xAxis\s*:/.test(html) || !/yAxis\s*:/.test(html)) {
        failures.push('axis_chart slot does not expose xAxis/yAxis')
      }
      break
    default:
      if (!hasGraphic(chart) || !hasRect(chart)) {
        failures.push(`${slotSpec.archetype} should preserve graphic rect surface`)
      }
      break
  }

  return {
    ok: failures.length === 0 && missingFeatures.length === 0,
    failures,
    missingFeatures,
    features: [...features],
  }
}

function styleBackground(chart) {
  return String(chart?.spec?.style?.background || '').toUpperCase()
}

function normalizeChartsResponse(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.charts)) return data.charts
  if (Array.isArray(data?.data?.charts)) return data.data.charts
  throw new Error('charts response must be an array or contain charts[]')
}

async function loadCharts(args) {
  if (args.chartsJson) {
    return normalizeChartsResponse(JSON.parse(fs.readFileSync(args.chartsJson, 'utf8')))
  }
  const response = await post('/get_charts', {
    uri: args.uri,
    worksheet_name: args.worksheet,
  })
  return normalizeChartsResponse(response)
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const charts = await loadCharts(args)
  if (!charts.length) throw new Error('No charts found for validation')

  const inferredPacks = new Map()
  for (const chart of charts) {
    const packId = getPackId(chart)
    if (packId) inferredPacks.set(packId, (inferredPacks.get(packId) || 0) + 1)
  }

  const expectedPack =
    args.expectedPack ||
    [...inferredPacks.entries()].sort((left, right) => right[1] - left[1])[0]?.[0] ||
    ''
  const pack = IMAGE_DERIVED_PACKS[expectedPack]
  if (!pack) throw new Error(`Unsupported or missing image-derived pack: ${expectedPack || '<empty>'}`)

  const warnings = []
  const errors = []
  const analyzed = charts.map((chart) => ({
    chart,
    rect: getChartRect(chart),
    packId: getPackId(chart),
  }))

  console.log(`[template-pack] expected=${expectedPack}`)
  console.log(`[charts] ${charts.length}`)

  for (const item of analyzed) {
    const title = item.chart.title || ''
    const rect = item.rect
    console.log(`[chart] ${item.chart.chart_id || item.chart.id || '<no-id>'} ${title}`)
    console.log(`  pack=${item.packId || '<missing>'} rect=${rect ? rectLabel(rect) : '<missing>'}`)
    if (item.packId && item.packId !== expectedPack) {
      warnings.push(`${item.chart.chart_id || title} pack ${item.packId} differs from expected ${expectedPack}`)
    }
    if (pack.requiredBackground && styleBackground(item.chart) !== pack.requiredBackground.toUpperCase()) {
      warnings.push(`${item.chart.chart_id || title} background ${item.chart?.spec?.style?.background || '<missing>'} differs from template ${pack.requiredBackground}`)
    }
  }

  let matchedSlots = 0
  let archetypePasses = 0
  let sectionBarCount = 0
  let totalHtmlLength = 0
  let uniformInsetCount = 0
  const usedChartIds = new Set()

  for (const slotSpec of pack.slots) {
    const slot = parseRange(slotSpec.from, slotSpec.to)
    const matches = analyzed
      .filter((item) => item.rect && chartFitsSlot(item.rect, slot, slotSpec.toleranceRows ?? 3))
      .sort((left, right) => distance(left.rect, slot) - distance(right.rect, slot))

    if (!matches.length) {
      errors.push(`missing near-slot match for ${slotSpec.slotId} (${slotSpec.archetype}) expected around ${rectLabel(slot)}`)
      continue
    }

    const best = matches.find((item) => !usedChartIds.has(item.chart.chart_id || item.chart.id)) || matches[0]
    usedChartIds.add(best.chart.chart_id || best.chart.id)
    matchedSlots += 1

    const title = best.chart.title || best.chart.chart_id || slotSpec.slotId
    const check = archetypeSatisfied(best.chart, slotSpec, pack)
    if (check.ok) archetypePasses += 1
    if (check.features.includes('section_bar')) sectionBarCount += 1
    totalHtmlLength += normalizeHtml(best.chart).length
    const offsetX = toFiniteNumber(best.chart?.format?.offset_x) ?? 0
    const offsetY = toFiniteNumber(best.chart?.format?.offset_y) ?? 0
    if (offsetX >= 12 && offsetY >= 8) uniformInsetCount += 1

    console.log(`[slot] ${slotSpec.slotId} ${slotSpec.archetype} -> ${title}`)
    console.log(`  features=${check.features.join(',') || '<none>'}`)

    if (!check.ok) {
      for (const failure of check.failures) {
        errors.push(`${slotSpec.slotId} (${title}) archetype failed: ${failure}`)
      }
      for (const feature of check.missingFeatures) {
        errors.push(`${slotSpec.slotId} (${title}) missing required visual feature: ${feature}`)
      }
    }

    const width = toFiniteNumber(best.chart?.dimension?.width) ?? toFiniteNumber(best.chart?.width)
    const slotWidth = (best.rect.toCol - best.rect.fromCol) * CELL_WIDTH_PX
    if (slotSpec.requiresLeftPadding && offsetX <= 0) {
      errors.push(`${slotSpec.slotId} (${title}) missing left offset_x padding`)
    }
    if (slotSpec.requiresRightPadding && width != null && width >= slotWidth) {
      errors.push(`${slotSpec.slotId} (${title}) width was not reduced for right inner padding`)
    }

    if (args.strictDensity) {
      const density = validateDensity(best.chart, slotSpec)
      console.log(
        `  density=html:${density.actual.htmlLength} rects:${density.actual.rectElements} texts:${density.actual.textElements} widths:${density.actual.widthRules}`,
      )
      for (const densityError of density.errors) {
        errors.push(`${slotSpec.slotId} (${title}) density failed: ${densityError}`)
      }
    }
  }

  const acceptance = pack.similarityAcceptance
  const graphicCardCount = analyzed.filter((item) => hasGraphic(item.chart) && hasRect(item.chart)).length
  const plainAxisCount = analyzed.filter((item) => hasPlainAxisRenderer(item.chart)).length
  const graphicCardRatio = graphicCardCount / charts.length
  const sectionBarRatio = sectionBarCount / Math.max(1, matchedSlots)
  const slotMatchRatio = matchedSlots / pack.slots.length
  const averageHtmlLength = totalHtmlLength / Math.max(1, matchedSlots)

  if (graphicCardRatio < acceptance.minGraphicCardRatio) {
    errors.push(
      `graphic/card renderer ratio ${graphicCardCount}/${charts.length} (${graphicCardRatio.toFixed(2)}) is below template minimum ${acceptance.minGraphicCardRatio}`,
    )
  }
  if (plainAxisCount > acceptance.maxPlainAxisModules) {
    errors.push(`plain axis modules ${plainAxisCount} exceed template maximum ${acceptance.maxPlainAxisModules}`)
  }
  if (sectionBarRatio < acceptance.requiredSectionBarRatio) {
    errors.push(
      `section bar ratio ${sectionBarCount}/${matchedSlots} (${sectionBarRatio.toFixed(2)}) is below template minimum ${acceptance.requiredSectionBarRatio}`,
    )
  }
  if (slotMatchRatio < acceptance.requiredSlotMatchRatio) {
    errors.push(
      `slot match ratio ${matchedSlots}/${pack.slots.length} (${slotMatchRatio.toFixed(2)}) is below template minimum ${acceptance.requiredSlotMatchRatio}`,
    )
  }
  if (args.strictDensity) {
    const densityAcceptance = pack.densityAcceptance || {}
    if (densityAcceptance.minAverageHtmlLength && averageHtmlLength < densityAcceptance.minAverageHtmlLength) {
      errors.push(
        `average renderer html length ${averageHtmlLength.toFixed(0)} is below density minimum ${densityAcceptance.minAverageHtmlLength}`,
      )
    }
    if (densityAcceptance.maxUniformInsetCharts != null && uniformInsetCount > densityAcceptance.maxUniformInsetCharts) {
      errors.push(
        `uniform all-side inset charts ${uniformInsetCount}/${matchedSlots} exceeds density maximum ${densityAcceptance.maxUniformInsetCharts}; use more of the slot area except for real gutters`,
      )
    }
  }

  console.log('[template-summary]')
  console.log(`  matched_slots: ${matchedSlots}/${pack.slots.length}`)
  console.log(`  archetype_passes: ${archetypePasses}/${matchedSlots}`)
  console.log(`  graphic_card_ratio: ${graphicCardCount}/${charts.length} (${graphicCardRatio.toFixed(2)})`)
  console.log(`  plain_axis_modules: ${plainAxisCount}`)
  console.log(`  section_bar_ratio: ${sectionBarCount}/${matchedSlots} (${sectionBarRatio.toFixed(2)})`)
  if (args.strictDensity) {
    console.log(`  average_html_length: ${averageHtmlLength.toFixed(0)}`)
    console.log(`  uniform_inset_charts: ${uniformInsetCount}/${matchedSlots}`)
  }

  for (const warning of warnings) console.log(`WARN: ${warning}`)
  for (const error of errors) console.log(`ERROR: ${error}`)
  console.log('[summary]')
  console.log(`  errors: ${errors.length}`)
  console.log(`  warnings: ${warnings.length}`)

  if (errors.length) process.exitCode = 1
}

main().catch((error) => {
  console.error(error.stack || error.message)
  process.exit(1)
})
