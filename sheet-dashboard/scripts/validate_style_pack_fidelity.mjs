#!/usr/bin/env node

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel'
const CELL_WIDTH_PX = 101
const CELL_HEIGHT_PX = 27

const PACKS = {
  'financial-board-report': {
    requiredBackground: '#F6F7F8',
    minCharts: 5,
    maxCharts: 7,
    slots: [
      { role: 'kpi', from: 'B6', to: 'N12', toleranceRows: 6 },
      { role: 'main_trend', from: 'B14', to: 'N25', toleranceRows: 6 },
      { role: 'left_card', from: 'B27', to: 'G37', requiresRightPadding: true, toleranceRows: 8 },
      { role: 'right_card', from: 'H27', to: 'M37', requiresLeftPadding: true, toleranceRows: 8 },
      { role: 'table', from: 'B39', to: 'N52', toleranceRows: 10 },
    ],
    avoidSignals: [
      {
        id: 'executive-summary-workbook',
        worksheetPatterns: [
          /老板摘要/,
          /executive\s*summary/i,
          /company\s*profile/i,
          /segment\s*revenue/i,
          /revenue\s*mix/i,
          /经营概览/,
        ],
        preferredPack: 'financial-teal-executive-summary-report',
      },
    ],
  },
  'financial-teal-executive-summary-report': {
    requiredBackground: '#EEF6F6',
    minCharts: 7,
    maxCharts: 10,
    slots: [
      { role: 'title', from: 'B2', to: 'N7', toleranceRows: 2 },
      { role: 'left_intro', from: 'B9', to: 'G17', requiresRightPadding: true, toleranceRows: 3 },
      { role: 'right_intro', from: 'H9', to: 'N17', requiresLeftPadding: true, toleranceRows: 3 },
      { role: 'kpis', from: 'B19', to: 'N25', toleranceRows: 3 },
      { role: 'left_mid', from: 'B27', to: 'G37', requiresRightPadding: true, toleranceRows: 4 },
      { role: 'right_mid', from: 'H27', to: 'N37', requiresLeftPadding: true, toleranceRows: 4 },
      { role: 'left_lower', from: 'B39', to: 'G49', requiresRightPadding: true, toleranceRows: 4 },
      { role: 'right_lower', from: 'H39', to: 'N49', requiresLeftPadding: true, toleranceRows: 4 },
      { role: 'followup', from: 'B51', to: 'N61', toleranceRows: 5 },
    ],
  },
}

function usage() {
  console.error(`Usage:
  node scripts/validate_style_pack_fidelity.mjs --uri <sheet_uri> --worksheet <worksheet_name> [options]

Options:
  --expected-pack <id>       Validate against this pack instead of inferring from charts.
  --source-worksheets <csv>  Optional source worksheet names for content-signal checks.
`)
}

function parseArgs(argv) {
  const args = {
    sourceWorksheets: [],
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
      case '--expected-pack':
        args.expectedPack = argv[index + 1]
        index += 1
        break
      case '--source-worksheets':
        args.sourceWorksheets = String(argv[index + 1] || '')
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean)
        index += 1
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
  for (const packId of Object.keys(PACKS)) {
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

function styleBackground(chart) {
  return String(chart?.spec?.style?.background || '').toUpperCase()
}

function hasGraphicCardRenderer(chart) {
  const html = String(chart.html || '')
  return /graphic\s*:/.test(html) && /type\s*:\s*['"]rect['"]/.test(html)
}

function hasPlainAxisRenderer(chart) {
  const html = String(chart.html || '')
  return /series\s*:/.test(html) && /xAxis\s*:/.test(html) && /yAxis\s*:/.test(html) && !hasGraphicCardRenderer(chart)
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const response = await post('/get_charts', {
    uri: args.uri,
    worksheet_name: args.worksheet,
  })
  const charts = Array.isArray(response.charts) ? response.charts : []
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
  const pack = PACKS[expectedPack]
  if (!pack) throw new Error(`Unsupported or missing expected pack: ${expectedPack || '<empty>'}`)

  const warnings = []
  const errors = []
  const analyzed = charts.map((chart) => ({
    chart,
    rect: getChartRect(chart),
    packId: getPackId(chart),
  }))

  console.log(`[pack] expected=${expectedPack}`)
  console.log(`[charts] ${charts.length}`)

  if (charts.length < pack.minCharts || charts.length > pack.maxCharts) {
    warnings.push(`chart count ${charts.length} differs from ${expectedPack} expected range ${pack.minCharts}-${pack.maxCharts}`)
  }

  for (const item of analyzed) {
    const style = item.chart?.spec?.style || {}
    const title = item.chart.title || ''
    const rect = item.rect
    console.log(`[chart] ${item.chart.chart_id} ${title}`)
    console.log(`  pack=${item.packId || '<missing>'} rect=${rect ? rectLabel(rect) : '<missing>'}`)
    if (!item.packId) {
      warnings.push(`${item.chart.chart_id} missing dashboard_style_pack_id; do not rely only on prose style_source`)
    } else if (item.packId !== expectedPack) {
      warnings.push(`${item.chart.chart_id} pack ${item.packId} differs from expected ${expectedPack}`)
    }
    if (pack.requiredBackground && styleBackground(item.chart) !== pack.requiredBackground.toUpperCase()) {
      warnings.push(`${item.chart.chart_id} background ${style.background || '<missing>'} differs from ${expectedPack} ${pack.requiredBackground}`)
    }
  }

  for (const slotSpec of pack.slots) {
    const slot = parseRange(slotSpec.from, slotSpec.to)
    const matches = analyzed
      .filter((item) => item.rect && chartFitsSlot(item.rect, slot, slotSpec.toleranceRows ?? 3))
      .sort((left, right) => distance(left.rect, slot) - distance(right.rect, slot))

    if (!matches.length) {
      warnings.push(`missing near-slot match for ${slotSpec.role} expected around ${rectLabel(slot)}`)
      continue
    }

    const best = matches[0]
    const offsetX = toFiniteNumber(best.chart?.format?.offset_x) ?? 0
    const width = toFiniteNumber(best.chart?.dimension?.width) ?? toFiniteNumber(best.chart?.width)
    const slotWidth = (best.rect.toCol - best.rect.fromCol) * CELL_WIDTH_PX

    if (slotSpec.requiresLeftPadding && offsetX <= 0) {
      warnings.push(`${best.chart.chart_id} matched ${slotSpec.role} but missing left offset_x padding`)
    }
    if (slotSpec.requiresRightPadding && width != null && width >= slotWidth) {
      warnings.push(`${best.chart.chart_id} matched ${slotSpec.role} but width was not reduced for right inner padding`)
    }
  }

  const plainAxisCount = analyzed.filter((item) => hasPlainAxisRenderer(item.chart)).length
  const cardRendererCount = analyzed.filter((item) => hasGraphicCardRenderer(item.chart)).length
  if (expectedPack === 'financial-teal-executive-summary-report' && cardRendererCount < Math.ceil(charts.length * 0.6)) {
    warnings.push(`too few graphic/card renderers for ${expectedPack}: ${cardRendererCount}/${charts.length}`)
  }
  if (expectedPack === 'financial-board-report' && plainAxisCount > 4) {
    warnings.push(`too many plain axis charts for report-style ${expectedPack}: ${plainAxisCount}/${charts.length}`)
  }

  const sourceNames = args.sourceWorksheets.join(' ')
  for (const signal of pack.avoidSignals || []) {
    if (signal.worksheetPatterns.some((pattern) => pattern.test(sourceNames))) {
      warnings.push(
        `source workbook signal ${signal.id} usually prefers ${signal.preferredPack}, not ${expectedPack}`,
      )
    }
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
