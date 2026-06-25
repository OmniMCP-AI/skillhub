#!/usr/bin/env node

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel'
const CELL_WIDTH_PX = 101
const CELL_HEIGHT_PX = 27
const DASHBOARD_FROM_COL = 1
const DASHBOARD_TO_COL = 14
const MAX_STANDARD_CHARTS_PER_ROW = 3
const DEFAULT_ROW_SPAN = 10
const VERTICAL_GAP_ROWS = 1
const FILTER_WIDGET_KINDS = new Set(['dropdown', 'input', 'date', 'date-preset', 'date-range', 'filter-list:filter'])

function usage() {
  console.error(`Usage:
  node scripts/validate_dashboard_layout.mjs --uri <sheet_uri> --worksheet <worksheet_name> [options]

Options:
  --chart-id <id>                 Validate only one chart. Repeatable.
  --fix-reset-layout              Reflow scanned charts and rewrite all of them with set_chart when layout drift is found.
  --respect-content-cells         Treat non-empty worksheet cells as blocked layout area.
`)
}

function parseArgs(argv) {
  const args = {
    chartIds: [],
    fixResetLayout: false,
    respectContentCells: false,
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
      case '--fix-reset-layout':
        args.fixResetLayout = true
        break
      case '--respect-content-cells':
        args.respectContentCells = true
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
  if (!token) {
    throw new Error('MAYBEAI_API_TOKEN is not set')
  }
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

function parseCell(cell) {
  const match = normalizeValue(cell).match(/^([A-Za-z]+)(\d+)$/)
  if (!match) return null
  const letters = match[1].toUpperCase()
  const rowNumber = Number(match[2])
  if (!Number.isFinite(rowNumber) || rowNumber < 1) return null

  let col = 0
  for (const char of letters) {
    col = col * 26 + (char.charCodeAt(0) - 64)
  }

  return { col: col - 1, row: rowNumber - 1 }
}

function parseObjectLiteral(source) {
  return new Function('"use strict"; return (' + source + ');')()
}

function buildRect(fromCol, fromRow, toCol, toRow) {
  return {
    fromCol,
    fromRow,
    toCol,
    toRow,
  }
}

function rectLabel(rect) {
  return `${toA1(rect.fromCol, rect.fromRow)}:${toA1(rect.toCol - 1, rect.toRow - 1)}`
}

function buildPxRect(left, top, right, bottom) {
  return { left, top, right, bottom }
}

function pxRectLabel(rect) {
  return `x:${Math.round(rect.left)}-${Math.round(rect.right)} y:${Math.round(rect.top)}-${Math.round(rect.bottom)}`
}

function pxRectsOverlap(left, right) {
  return !(
    left.right <= right.left ||
    right.right <= left.left ||
    left.bottom <= right.top ||
    right.bottom <= left.top
  )
}

function spansFromSize(chart) {
  const width =
    toFiniteNumber(chart?.dimension?.width) ??
    toFiniteNumber(chart?.width) ??
    CELL_WIDTH_PX * 13
  const height =
    toFiniteNumber(chart?.dimension?.height) ??
    toFiniteNumber(chart?.height) ??
    CELL_HEIGHT_PX * DEFAULT_ROW_SPAN

  return {
    spanCols: Math.max(1, Math.min(13, Math.round(width / CELL_WIDTH_PX) || 13)),
    spanRows: Math.max(1, Math.round(height / CELL_HEIGHT_PX) || DEFAULT_ROW_SPAN),
  }
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
    return buildRect(fromCol, fromRow, toCol, toRow)
  }

  const anchor = parseCell(chart?.cell)
  if (!anchor) return null
  const spans = spansFromSize(chart)
  return buildRect(
    anchor.col,
    anchor.row,
    anchor.col + spans.spanCols,
    anchor.row + spans.spanRows,
  )
}

function getChartVisualRectPx(chart, rect) {
  if (!rect) return null
  const format = chart?.format || {}
  const offsetX = toFiniteNumber(format.offset_x) ?? 0
  const offsetY = toFiniteNumber(format.offset_y) ?? 0
  const width =
    toFiniteNumber(chart?.dimension?.width) ??
    toFiniteNumber(chart?.width) ??
    (rect.toCol - rect.fromCol) * CELL_WIDTH_PX
  const height =
    toFiniteNumber(chart?.dimension?.height) ??
    toFiniteNumber(chart?.height) ??
    (rect.toRow - rect.fromRow) * CELL_HEIGHT_PX
  const left = rect.fromCol * CELL_WIDTH_PX + offsetX
  const top = rect.fromRow * CELL_HEIGHT_PX + offsetY
  return buildPxRect(left, top, left + width, top + height)
}

function getGridRectPx(rect) {
  if (!rect) return null
  return buildPxRect(
    rect.fromCol * CELL_WIDTH_PX,
    rect.fromRow * CELL_HEIGHT_PX,
    rect.toCol * CELL_WIDTH_PX,
    rect.toRow * CELL_HEIGHT_PX,
  )
}

function pxRectInside(inner, outer) {
  return (
    inner.left >= outer.left &&
    inner.top >= outer.top &&
    inner.right <= outer.right &&
    inner.bottom <= outer.bottom
  )
}

function getChartSpans(chart, rect) {
  if (rect) {
    return {
      spanCols: Math.max(1, Math.min(13, rect.toCol - rect.fromCol)),
      spanRows: Math.max(1, rect.toRow - rect.fromRow),
    }
  }
  return spansFromSize(chart)
}

function isInsideDashboard(rect) {
  return rect.fromCol >= DASHBOARD_FROM_COL && rect.toCol <= DASHBOARD_TO_COL
}

function rectsOverlap(left, right) {
  return !(
    left.toCol <= right.fromCol ||
    right.toCol <= left.fromCol ||
    left.toRow <= right.fromRow ||
    right.toRow <= left.fromRow
  )
}

function rectsHorizontallyIntersect(left, right) {
  return !(left.toCol <= right.fromCol || right.toCol <= left.fromCol)
}

function cellValueIsNonEmpty(value) {
  return normalizeValue(value) !== ''
}

function buildBlockedRectsFromReadSheet(readSheetResponse) {
  const values = Array.isArray(readSheetResponse?.values) ? readSheetResponse.values : []
  const blockedRects = []
  for (let rowIndex = 0; rowIndex < values.length; rowIndex += 1) {
    const row = Array.isArray(values[rowIndex]) ? values[rowIndex] : []
    for (let colIndex = 0; colIndex < row.length; colIndex += 1) {
      if (!cellValueIsNonEmpty(row[colIndex])) continue
      blockedRects.push(buildRect(colIndex, rowIndex, colIndex + 1, rowIndex + 1))
    }
  }
  return blockedRects
}

function rectOverlapsAnyBlockedCell(rect, blockedRects) {
  return blockedRects.some((blockedRect) => rectsOverlap(rect, blockedRect))
}

function computeContentAwareStart(blockedRects) {
  if (!blockedRects.length) {
    return {
      startRow: 1,
      startCol: DASHBOARD_FROM_COL,
      placementMode: 'default-grid',
    }
  }

  const occupiedBounds = blockedRects.reduce(
    (acc, rect) => ({
      maxCol: Math.max(acc.maxCol, rect.toCol - 1),
      maxRow: Math.max(acc.maxRow, rect.toRow - 1),
    }),
    { maxCol: -1, maxRow: -1 },
  )

  const rightStartCol = Math.max(DASHBOARD_FROM_COL, occupiedBounds.maxCol + 1)
  const remainingCols = DASHBOARD_TO_COL - rightStartCol
  if (remainingCols >= 4) {
    return {
      startRow: 0,
      startCol: rightStartCol,
      placementMode: 'same-sheet-right',
    }
  }

  return {
    startRow: occupiedBounds.maxRow + 1 + VERTICAL_GAP_ROWS,
    startCol: DASHBOARD_FROM_COL,
    placementMode: 'same-sheet-below',
  }
}

function getWidgetEmitters(chart) {
  if (normalizeValue(chart.type).toLowerCase() !== 'json') return []
  if (!normalizeValue(chart.html)) return []

  let config
  try {
    config = parseObjectLiteral(chart.html)
  } catch {
    return []
  }

  if (!config || config.library !== 'shadcn') return []

  const emitters = []

  if (config.component === 'dropdown') {
    const emitConfig = config?.props?.onChange
    const source = config?.props?.source
    if (emitConfig?.event && source?.valueField) {
      emitters.push({
        chartId: chart.chart_id,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'dropdown',
      })
    }
  }

  if (config.component === 'input') {
    const emitConfig = config?.props?.onChange
    if (emitConfig?.event) {
      emitters.push({
        chartId: chart.chart_id,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'input',
      })
    }
  }

  if (config.component === 'date') {
    const emitConfig = config?.props?.onChange
    const source = config?.props?.source
    if (emitConfig?.event && (source?.valueField || source?.endField || source?.startField)) {
      emitters.push({
        chartId: chart.chart_id,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind:
          config?.props?.selectionMode === 'preset'
            ? 'date-preset'
            : config?.props?.selectionMode === 'range'
              ? 'date-range'
              : 'date',
      })
    }
  }

  if (config.component === 'filter-list') {
    const emitConfig = config?.props?.filter?.onChange?.emitEvent
    const source = config?.props?.filter?.source
    if (emitConfig?.event && source?.valueField) {
      emitters.push({
        chartId: chart.chart_id,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'filter-list:filter',
      })
    }
  }

  return emitters
}

function receiveConfigMatchesEmitter(receiveConfig, emitter) {
  if (normalizeValue(receiveConfig?.event) !== normalizeValue(emitter?.event)) return false
  if (receiveConfig?.name && normalizeValue(receiveConfig.name) !== normalizeValue(emitter?.name)) return false
  if (receiveConfig?.key && emitter?.key && normalizeValue(receiveConfig.key) !== normalizeValue(emitter.key)) return false
  return true
}

function buildChartPayload(chart, overrides) {
  const payload = {
    chart_id: chart.chart_id,
    type: chart.type,
    title: chart.title,
    legend: chart.legend,
    x_axis_name: chart.x_axis_name,
    y_axis_name: chart.y_axis_name,
    width: overrides.width ?? chart.dimension?.width ?? chart.width,
    height: overrides.height ?? chart.dimension?.height ?? chart.height,
    show_blanks: chart.show_blanks,
    sql: overrides.sql ?? chart.sql,
    spec: overrides.spec ?? chart.spec,
    html: overrides.html ?? chart.html,
    format: overrides.format ?? chart.format,
  }
  return Object.fromEntries(Object.entries(payload).filter(([, value]) => value != null))
}

async function setChart(uri, worksheetName, chart, overrides) {
  return await post('/set_chart', {
    uri,
    worksheet_name: worksheetName,
    cell: overrides.cell ?? chart.cell,
    chart: buildChartPayload(chart, overrides),
  })
}

function analyzeChart(chart, index) {
  const rect = getChartRect(chart)
  const visualRectPx = getChartVisualRectPx(chart, rect)
  const gridRectPx = getGridRectPx(rect)
  const spans = getChartSpans(chart, rect)
  const issues = []
  const expectedCell = rect ? toA1(rect.fromCol, rect.fromRow) : null

  if (!rect) {
    issues.push('missing-layout-anchor')
  } else {
    if (!isInsideDashboard(rect)) {
      issues.push('outside-dashboard-bounds')
    }
    if (expectedCell && normalizeValue(chart.cell) && normalizeValue(chart.cell) !== expectedCell) {
      issues.push('cell-format-mismatch')
    }
    if (visualRectPx && gridRectPx && !pxRectInside(visualRectPx, gridRectPx)) {
      issues.push('visual-rect-outside-grid-slot')
    }
  }

  return {
    chart,
    index,
    rect,
    visualRectPx,
    gridRectPx,
    spans,
    expectedCell,
    issues,
    emitters: getWidgetEmitters(chart),
  }
}

function baseSortItems(left, right) {
  const leftRow = left.rect?.fromRow ?? Number.MAX_SAFE_INTEGER
  const rightRow = right.rect?.fromRow ?? Number.MAX_SAFE_INTEGER
  if (leftRow !== rightRow) return leftRow - rightRow

  const leftCol = left.rect?.fromCol ?? Number.MAX_SAFE_INTEGER
  const rightCol = right.rect?.fromCol ?? Number.MAX_SAFE_INTEGER
  if (leftCol !== rightCol) return leftCol - rightCol

  return left.index - right.index
}

function buildFilterLinks(items) {
  const itemByChartId = new Map(items.map((item) => [item.chart.chart_id, item]))
  const links = []

  for (const item of items) {
    for (const emitter of item.emitters || []) {
      if (!FILTER_WIDGET_KINDS.has(emitter.kind)) continue
      for (const candidate of items) {
        if (candidate.chart.chart_id === item.chart.chart_id) continue
        const receiveConfigs = Array.isArray(candidate.chart?.spec?.interaction?.receive)
          ? candidate.chart.spec.interaction.receive
          : []
        if (!receiveConfigs.some((receiveConfig) => receiveConfigMatchesEmitter(receiveConfig, emitter))) {
          continue
        }
        if (!itemByChartId.has(candidate.chart.chart_id)) continue
        links.push({
          filter: item,
          linked: candidate,
          emitter,
        })
      }
    }
  }

  return links
}

function sortForReflow(items, filterLinks) {
  const itemById = new Map(items.map((item) => [item.chart.chart_id, item]))
  const inDegree = new Map(items.map((item) => [item.chart.chart_id, 0]))
  const outgoing = new Map(items.map((item) => [item.chart.chart_id, new Set()]))

  for (const link of filterLinks) {
    const fromId = link.filter.chart.chart_id
    const toId = link.linked.chart.chart_id
    if (!itemById.has(fromId) || !itemById.has(toId)) continue
    if (outgoing.get(fromId).has(toId)) continue
    outgoing.get(fromId).add(toId)
    inDegree.set(toId, (inDegree.get(toId) || 0) + 1)
  }

  const ready = items
    .filter((item) => (inDegree.get(item.chart.chart_id) || 0) === 0)
    .sort(baseSortItems)
  const ordered = []

  while (ready.length) {
    const next = ready.shift()
    ordered.push(next)
    const nextIds = [...(outgoing.get(next.chart.chart_id) || [])]
    nextIds.sort((leftId, rightId) => baseSortItems(itemById.get(leftId), itemById.get(rightId)))
    for (const linkedId of nextIds) {
      inDegree.set(linkedId, (inDegree.get(linkedId) || 0) - 1)
      if ((inDegree.get(linkedId) || 0) === 0) {
        ready.push(itemById.get(linkedId))
        ready.sort(baseSortItems)
      }
    }
  }

  if (ordered.length !== items.length) {
    return [...items].sort(baseSortItems)
  }

  return ordered
}

function buildLayoutFixes(items, filterLinks, blockedRects = []) {
  const ordered = sortForReflow(items, filterLinks)
  const startRow =
    ordered.reduce((min, item) => {
      const row = item.rect?.fromRow
      return row != null ? Math.min(min, row) : min
    }, Number.MAX_SAFE_INTEGER) || 1
  const contentAwareStart = computeContentAwareStart(blockedRects)

  let cursorRow = blockedRects.length
    ? contentAwareStart.startRow
    : Number.isFinite(startRow) && startRow !== Number.MAX_SAFE_INTEGER
      ? startRow
      : 1
  let cursorCol = blockedRects.length ? contentAwareStart.startCol : DASHBOARD_FROM_COL
  let rowHeight = 0
  let rowCount = 0
  const fixes = []

  for (const item of ordered) {
    const spanCols = Math.max(1, Math.min(13, item.spans.spanCols))
    const spanRows = Math.max(1, item.spans.spanRows)
    const isFullWidth = spanCols >= 13
    const remainingCols = DASHBOARD_TO_COL - cursorCol

    if (
      cursorCol !== DASHBOARD_FROM_COL &&
      (isFullWidth || spanCols > remainingCols || rowCount >= MAX_STANDARD_CHARTS_PER_ROW)
    ) {
      cursorRow += rowHeight + VERTICAL_GAP_ROWS
      cursorCol = DASHBOARD_FROM_COL
      rowHeight = 0
      rowCount = 0
    }

    let rect = buildRect(
      cursorCol,
      cursorRow,
      Math.min(DASHBOARD_TO_COL, cursorCol + spanCols),
      cursorRow + spanRows,
    )

    while (blockedRects.length > 0 && rectOverlapsAnyBlockedCell(rect, blockedRects)) {
      cursorRow += Math.max(rowHeight, 1) + VERTICAL_GAP_ROWS
      cursorCol = DASHBOARD_FROM_COL
      rowHeight = 0
      rowCount = 0
      rect = buildRect(
        cursorCol,
        cursorRow,
        Math.min(DASHBOARD_TO_COL, cursorCol + spanCols),
        cursorRow + spanRows,
      )
    }

    fixes.push({
      item,
      rect,
      cell: toA1(rect.fromCol, rect.fromRow),
      width:
        toFiniteNumber(item.chart?.dimension?.width) ??
        toFiniteNumber(item.chart?.width) ??
        (rect.toCol - rect.fromCol) * CELL_WIDTH_PX,
      height:
        toFiniteNumber(item.chart?.dimension?.height) ??
        toFiniteNumber(item.chart?.height) ??
        (rect.toRow - rect.fromRow) * CELL_HEIGHT_PX,
      format: {
        ...(item.chart.format || {}),
        from: {
          ...(item.chart.format?.from || {}),
          col: rect.fromCol,
          row: rect.fromRow,
          col_off: 0,
          row_off: 0,
        },
        to: {
          ...(item.chart.format?.to || {}),
          col: rect.toCol,
          row: rect.toRow,
          col_off: 0,
          row_off: 0,
        },
      },
    })

    cursorCol = rect.toCol
    rowHeight = Math.max(rowHeight, spanRows)
    rowCount += 1

    if (
      isFullWidth ||
      rowCount >= MAX_STANDARD_CHARTS_PER_ROW ||
      cursorCol >= DASHBOARD_TO_COL
    ) {
      cursorRow += rowHeight + VERTICAL_GAP_ROWS
      cursorCol = DASHBOARD_FROM_COL
      rowHeight = 0
      rowCount = 0
    }
  }

  return fixes
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const response = await post('/get_charts', {
    uri: args.uri,
    worksheet_name: args.worksheet,
  })
  const readSheetResponse = args.respectContentCells
    ? await post('/read_sheet', {
        uri: args.uri,
        worksheet_name: args.worksheet,
      })
    : null
  const blockedRects = readSheetResponse ? buildBlockedRectsFromReadSheet(readSheetResponse) : []

  const charts = Array.isArray(response.charts) ? response.charts : []
  const filteredCharts =
    args.chartIds.length > 0
      ? charts.filter((chart) => args.chartIds.includes(chart.chart_id))
      : charts

  if (!filteredCharts.length) {
    throw new Error('No charts found for validation')
  }

  const analyzed = filteredCharts.map((chart, index) => analyzeChart(chart, index))
  const warnings = []
  const overlaps = []
  const filterLinks = buildFilterLinks(analyzed)

  for (const item of analyzed) {
    const title = item.chart.title || ''
    console.log(`\n[chart] ${item.chart.chart_id} ${title}`.trim())
    if (item.rect) {
      if (blockedRects.length > 0 && rectOverlapsAnyBlockedCell(item.rect, blockedRects)) {
        const message = `${item.chart.chart_id} ${rectLabel(item.rect)} overlaps existing content cells`
        warnings.push(message)
        console.log(`  warning: ${message}`)
      }
      console.log(`  rect: ${rectLabel(item.rect)}`)
      if (item.visualRectPx) {
        const offsetX = toFiniteNumber(item.chart?.format?.offset_x) ?? 0
        const offsetY = toFiniteNumber(item.chart?.format?.offset_y) ?? 0
        console.log(`  visual: ${pxRectLabel(item.visualRectPx)} offset=${offsetX},${offsetY}`)
      }
      console.log(`  cell: ${normalizeValue(item.chart.cell) || '(empty)'} -> expected ${item.expectedCell}`)
    } else {
      console.log(`  rect: (missing)`)
    }
    for (const issue of item.issues) {
      const message = `${item.chart.chart_id} ${issue}`
      warnings.push(message)
      console.log(`  warning: ${message}`)
    }
  }

  for (let leftIndex = 0; leftIndex < analyzed.length; leftIndex += 1) {
    const left = analyzed[leftIndex]
    if (!left.rect) continue
    for (let rightIndex = leftIndex + 1; rightIndex < analyzed.length; rightIndex += 1) {
      const right = analyzed[rightIndex]
      if (!right.rect) continue
      if (!rectsOverlap(left.rect, right.rect)) continue
      overlaps.push([left, right])
      const message =
        `${left.chart.chart_id} ${rectLabel(left.rect)} overlaps ` +
        `${right.chart.chart_id} ${rectLabel(right.rect)}`
      warnings.push(message)
      console.log(`  warning: ${message}`)
    }
  }

  for (let leftIndex = 0; leftIndex < analyzed.length; leftIndex += 1) {
    const left = analyzed[leftIndex]
    if (!left.visualRectPx) continue
    for (let rightIndex = leftIndex + 1; rightIndex < analyzed.length; rightIndex += 1) {
      const right = analyzed[rightIndex]
      if (!right.visualRectPx) continue
      if (!pxRectsOverlap(left.visualRectPx, right.visualRectPx)) continue
      const message =
        `${left.chart.chart_id} visual ${pxRectLabel(left.visualRectPx)} overlaps ` +
        `${right.chart.chart_id} visual ${pxRectLabel(right.visualRectPx)}`
      warnings.push(message)
      console.log(`  warning: ${message}`)
    }
  }

  for (let upperIndex = 0; upperIndex < analyzed.length; upperIndex += 1) {
    const upper = analyzed[upperIndex]
    if (!upper.rect) continue
    for (let lowerIndex = 0; lowerIndex < analyzed.length; lowerIndex += 1) {
      if (upperIndex === lowerIndex) continue
      const lower = analyzed[lowerIndex]
      if (!lower.rect) continue
      if (upper.rect.fromRow > lower.rect.fromRow) continue
      if (!rectsHorizontallyIntersect(upper.rect, lower.rect)) continue
      if (rectsOverlap(upper.rect, lower.rect)) continue
      if (lower.rect.fromRow >= upper.rect.toRow + VERTICAL_GAP_ROWS) continue
      const message =
        `${upper.chart.chart_id} ${rectLabel(upper.rect)} should keep ${VERTICAL_GAP_ROWS} empty row above ` +
        `${lower.chart.chart_id} ${rectLabel(lower.rect)}`
      warnings.push(message)
      console.log(`  warning: ${message}`)
    }
  }

  for (const link of filterLinks) {
    if (!link.filter.rect || !link.linked.rect) continue
    if (link.filter.rect.toRow + VERTICAL_GAP_ROWS <= link.linked.rect.fromRow) continue
    const message =
      `${link.filter.chart.chart_id} ${rectLabel(link.filter.rect)} should be above ` +
      `${link.linked.chart.chart_id} ${rectLabel(link.linked.rect)}`
    warnings.push(message)
    console.log(`  warning: ${message}`)
  }

  if (args.fixResetLayout && warnings.length) {
    const fixes = buildLayoutFixes(analyzed, filterLinks, blockedRects)
    console.log(`\n[fix] rewriting ${fixes.length} charts with reflowed layout`)
    for (const fix of fixes) {
      await setChart(args.uri, args.worksheet, fix.item.chart, {
        cell: fix.cell,
        format: fix.format,
        width: fix.width,
        height: fix.height,
      })
      console.log(`  patched: ${fix.item.chart.chart_id} -> ${rectLabel(fix.rect)}`)
    }
  }

  console.log('\n[summary]')
  console.log(`  charts scanned: ${filteredCharts.length}`)
  console.log(`  warnings: ${warnings.length}`)
  console.log(`  overlaps: ${overlaps.length}`)
  console.log(`  updates: ${args.fixResetLayout && warnings.length ? filteredCharts.length : 0}`)

  if (warnings.length && !args.fixResetLayout) {
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(error.message || String(error))
  process.exit(1)
})
