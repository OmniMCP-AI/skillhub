#!/usr/bin/env node

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel'

function usage() {
  console.error(`Usage:
  node scripts/validate_interaction_chart_sql.mjs --uri <sheet_uri> --worksheet <worksheet_name> [options]

Options:
  --chart-id <id>                 Validate only one chart. Repeatable.
  --sample-limit <n>              Number of sample values per filter emitter. Default: 2
  --filter <name=value>           Provide an explicit sample filter value. Repeatable.
  --fix-reset-outer-sql           Reset chart.sql to the resolved default-state SQL, or stripped baseSql when no defaults exist.
  --no-formula-check              Skip calc_formulas verification.
`)
}

function parseArgs(argv) {
  const args = {
    chartIds: [],
    filters: new Map(),
    sampleLimit: 2,
    fixResetOuterSql: false,
    verifyFormula: true,
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
      case '--sample-limit':
        args.sampleLimit = Math.max(1, Number(argv[index + 1]) || 2)
        index += 1
        break
      case '--filter': {
        const raw = argv[index + 1] || ''
        const splitAt = raw.indexOf('=')
        if (splitAt === -1) {
          throw new Error(`Invalid --filter value: ${raw}`)
        }
        const name = raw.slice(0, splitAt).trim()
        const value = raw.slice(splitAt + 1)
        if (!name) {
          throw new Error(`Invalid --filter value: ${raw}`)
        }
        args.filters.set(name, value)
        index += 1
        break
      }
      case '--fix-reset-outer-sql':
        args.fixResetOuterSql = true
        break
      case '--no-formula-check':
        args.verifyFormula = false
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

function normalizeSql(sql) {
  return String(sql || '')
    .replace(/\s+/g, ' ')
    .trim()
}

function stripInteractionPlaceholders(sql) {
  return normalizeSql(String(sql || '').replace(/__[A-Z0-9_]+__/g, ''))
}

function buildSqlFormula(sql) {
  const trimmed = normalizeSql(sql)
  return `=SQL("${trimmed.replace(/"/g, '""')}")`
}

function toSqlLiteral(value) {
  if (value == null) return 'NULL'
  if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  if (typeof value === 'boolean') return value ? 'TRUE' : 'FALSE'
  return `'${String(value).replace(/'/g, "''")}'`
}

function normalizeValue(value) {
  return String(value ?? '').trim()
}

function getFilterId(config) {
  return (
    normalizeValue(config?.name) ||
    `${normalizeValue(config?.event)}::${normalizeValue(config?.key)}`
  )
}

function parseIsoDate(value) {
  const normalized = normalizeValue(value)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(normalized)) return null
  const parsed = new Date(`${normalized}T00:00:00`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function formatIsoDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function shiftIsoDate(value, amount) {
  const parsed = parseIsoDate(value)
  if (!parsed) return normalizeValue(value)
  const next = new Date(parsed)
  if (amount?.months) {
    next.setMonth(next.getMonth() - amount.months)
    next.setDate(next.getDate() + 1)
  }
  if (amount?.days) {
    next.setDate(next.getDate() - (amount.days - 1))
  }
  return formatIsoDate(next)
}

function parseObjectLiteral(source) {
  return new Function('"use strict"; return (' + source + ');')()
}

function tableToRows(table) {
  if (!Array.isArray(table) || table.length < 2) return []
  const headerRow = Array.isArray(table[0]) ? table[0] : []
  const headers = headerRow.map((header, index) => normalizeValue(header) || `col${index + 1}`)
  return table.slice(1).map((row) => {
    const record = {}
    headers.forEach((header, index) => {
      record[header] = Array.isArray(row) ? row[index] : undefined
    })
    return record
  })
}

const compiledFunctionCache = new Map()

function compileFunction(source) {
  const key = String(source || '').trim()
  if (!key) {
    throw new Error('Cannot compile empty function source')
  }
  if (compiledFunctionCache.has(key)) {
    return compiledFunctionCache.get(key)
  }
  const fn = new Function('"use strict"; return (' + key + ');')()
  if (typeof fn !== 'function') {
    throw new Error('Configured source did not evaluate to a function')
  }
  compiledFunctionCache.set(key, fn)
  return fn
}

function runtimeEventMatches(receiveConfig, runtimeEvent) {
  if (normalizeValue(receiveConfig.event) !== normalizeValue(runtimeEvent.event)) {
    return false
  }
  if (receiveConfig.name && normalizeValue(receiveConfig.name) !== normalizeValue(runtimeEvent.name)) {
    return false
  }
  if (receiveConfig.key && runtimeEvent.key && normalizeValue(receiveConfig.key) !== normalizeValue(runtimeEvent.key)) {
    return false
  }
  return true
}

function buildActiveFilterContext(receiveConfigs, runtimeEvents) {
  const activeFilters = {}
  const filterValues = {}

  for (const receiveConfig of receiveConfigs) {
    const filterId = normalizeValue(receiveConfig.name) || `${normalizeValue(receiveConfig.event)}::${normalizeValue(receiveConfig.key)}`
    const runtimeEvent = runtimeEvents.get(filterId)
    if (!runtimeEvent) continue
    const key = normalizeValue(receiveConfig.key) || normalizeValue(runtimeEvent.key) || undefined
    const value = runtimeEvent.payload?.value ?? runtimeEvent.value
    activeFilters[filterId] = {
      filterId,
      ...(receiveConfig.name ? { name: normalizeValue(receiveConfig.name) } : {}),
      ...(key ? { key } : {}),
      value,
      payload: runtimeEvent.payload || {},
      event: runtimeEvent,
      sourceChartId: runtimeEvent.sourceChartId,
    }
    filterValues[filterId] = value
  }

  return { activeFilters, filterValues }
}

function applyReceiveSqlTransform(chart, receiveConfig, runtimeEvent, options) {
  const currentSql = normalizeSql(chart.sql)
  const baseSql =
    normalizeSql(options?.baseSql) ||
    normalizeSql(chart?.spec?.interaction?.baseSql) ||
    currentSql
  const currentWorkingSql = normalizeSql(options?.currentSql) || currentSql

  if (!runtimeEventMatches(receiveConfig, runtimeEvent)) {
    return currentWorkingSql
  }

  if (!normalizeValue(receiveConfig.sqlTransform)) {
    return currentWorkingSql
  }

  const sqlTransform = compileFunction(receiveConfig.sqlTransform)
  const result = sqlTransform(baseSql, {
    chart,
    event: runtimeEvent,
    helpers: { toSqlLiteral },
    key: normalizeValue(receiveConfig.key) || runtimeEvent.key,
    value: runtimeEvent.payload?.value ?? runtimeEvent.value,
    baseSql,
    currentSql: currentWorkingSql,
    activeFilters: options?.activeFilters || {},
    filterValues: options?.filterValues || {},
  })

  if (typeof result === 'string') {
    return normalizeSql(result)
  }
  if (result && typeof result === 'object' && typeof result.sql === 'string') {
    return normalizeSql(result.sql)
  }
  return currentWorkingSql
}

function rebuildSqlFromScenario(chart, receiveConfigs, runtimeEvents) {
  const baseSql = normalizeSql(chart?.spec?.interaction?.baseSql) || normalizeSql(chart.sql)
  const { activeFilters, filterValues } = buildActiveFilterContext(receiveConfigs, runtimeEvents)
  let nextSql = baseSql

  for (const receiveConfig of receiveConfigs) {
    const filterId = normalizeValue(receiveConfig.name) || `${normalizeValue(receiveConfig.event)}::${normalizeValue(receiveConfig.key)}`
    const runtimeEvent = runtimeEvents.get(filterId)
    if (!runtimeEvent) continue
    nextSql = applyReceiveSqlTransform(
      { ...chart, sql: nextSql },
      receiveConfig,
      runtimeEvent,
      {
        baseSql,
        currentSql: nextSql,
        activeFilters,
        filterValues,
      },
    )
  }

  return normalizeSql(nextSql)
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
        title: chart.title,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'dropdown',
        sourceChart: chart,
        valueField: source.valueField,
        defaultValue: normalizeValue(config?.props?.defaultValue),
        emptyWhen: emitConfig.value?.emptyWhen || [],
      })
    }
  }

  if (config.component === 'input') {
    const emitConfig = config?.props?.onChange
    if (emitConfig?.event) {
      emitters.push({
        chartId: chart.chart_id,
        title: chart.title,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'input',
        sourceChart: chart,
        defaultValue: normalizeValue(config?.props?.defaultValue),
        emptyWhen: emitConfig.value?.emptyWhen || [],
      })
    }
  }

  if (config.component === 'date') {
    const emitConfig = config?.props?.onChange
    const source = config?.props?.source
    if (emitConfig?.event && (source?.valueField || source?.endField)) {
      emitters.push({
        chartId: chart.chart_id,
        title: chart.title,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind:
          config?.props?.selectionMode === 'preset'
            ? 'date-preset'
            : config?.props?.selectionMode === 'range'
              ? 'date-range'
              : 'date',
        sourceChart: chart,
        valueField: source?.valueField || source?.endField,
        startField: source?.startField,
        endField: source?.endField || source?.valueField,
        presetOptions: Array.isArray(config?.props?.presetOptions)
          ? config.props.presetOptions
          : [],
        defaultStartValue: normalizeValue(config?.props?.defaultStartValue),
        defaultEndValue: normalizeValue(config?.props?.defaultEndValue),
        defaultPresetValue: normalizeValue(config?.props?.defaultPresetValue),
        emptyWhen: emitConfig.value?.emptyWhen || [],
      })
    }
  }

  if (config.component === 'list') {
    const emitConfig = config?.props?.onItemClick?.emitEvent
    if (emitConfig?.event && emitConfig?.valueField) {
      emitters.push({
        chartId: chart.chart_id,
        title: chart.title,
        event: emitConfig.event,
        name: emitConfig.name,
        key: emitConfig.key,
        kind: 'list',
        sourceChart: chart,
        valueField: emitConfig.valueField,
        emptyWhen: emitConfig.emptyWhen || [],
      })
    }
  }

  if (config.component === 'filter-list') {
    const filterEmitConfig = config?.props?.filter?.onChange?.emitEvent
    const filterSource = config?.props?.filter?.source
    if (filterEmitConfig?.event && filterSource?.valueField) {
      emitters.push({
        chartId: chart.chart_id,
        title: chart.title,
        event: filterEmitConfig.event,
        name: filterEmitConfig.name,
        key: filterEmitConfig.key,
        kind: 'filter-list:filter',
        sourceChart: chart,
        valueField: filterSource.valueField,
        emptyWhen: filterEmitConfig.value?.emptyWhen || [],
      })
    }

    const listEmitConfig = config?.props?.list?.onItemClick?.emitEvent
    if (listEmitConfig?.event && listEmitConfig?.valueField) {
      emitters.push({
        chartId: chart.chart_id,
        title: chart.title,
        event: listEmitConfig.event,
        name: listEmitConfig.name,
        key: listEmitConfig.key,
        kind: 'filter-list:list',
        sourceChart: chart,
        valueField: listEmitConfig.valueField,
        emptyWhen: listEmitConfig.emptyWhen || [],
      })
    }
  }

  return emitters
}

async function fetchSqlRows(uri, sql) {
  const payload = {
    uri,
    formulas: [
      {
        cell: 'A1',
        formula: buildSqlFormula(sql),
      },
    ],
  }
  const data = await post('/calc_formulas', payload)
  const result = Array.isArray(data.results) ? data.results[0] : null
  if (result?.error) {
    throw new Error(result.error)
  }
  return tableToRows(result?.range_values || [])
}

async function compileSql(uri, sql) {
  return await post('/sql/compile', { uri, sql })
}

async function verifyFormula(uri, sql) {
  return await post('/calc_formulas', {
    uri,
    formulas: [
      {
        cell: 'A1',
        formula: buildSqlFormula(sql),
      },
    ],
  })
}

function buildChartPayload(chart, overrides) {
  const payload = {
    chart_id: chart.chart_id,
    type: chart.type,
    title: chart.title,
    legend: chart.legend,
    x_axis_name: chart.x_axis_name,
    y_axis_name: chart.y_axis_name,
    width: chart.dimension?.width || chart.width,
    height: chart.dimension?.height || chart.height,
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
    cell: chart.cell,
    chart: buildChartPayload(chart, overrides),
  })
}

function createRuntimeEvent(sample, receiveConfig) {
  return {
    event: receiveConfig.event,
    name: receiveConfig.name,
    key: receiveConfig.key,
    value: sample.value,
    payload: {
      name: receiveConfig.name,
      key: receiveConfig.key,
      value: sample.value,
      ...(sample.payload && typeof sample.payload === 'object'
        ? sample.payload
        : {}),
    },
    sourceChartId: sample.sourceChartId,
    sourceChartType: sample.sourceChartType,
    sourceWorksheetName: sample.sourceWorksheetName,
  }
}

function getInteractionDefaultEntry(defaults, filterId) {
  if (!defaults || typeof defaults !== 'object') return undefined
  return defaults[filterId]
}

function getInteractionDefaultValue(defaultEntry) {
  if (defaultEntry == null) return ''
  if (typeof defaultEntry === 'object') {
    const value = normalizeValue(defaultEntry.value)
    if (value) return value
    const startDate = normalizeValue(defaultEntry.startDate)
    const endDate = normalizeValue(defaultEntry.endDate)
    if (startDate && endDate) return `${startDate}|${endDate}`
    const preset = normalizeValue(defaultEntry.preset)
    if (preset) return preset
  }
  return normalizeValue(defaultEntry)
}

function buildInteractionDefaultSample(defaultEntry, worksheetName, filterId) {
  const value = getInteractionDefaultValue(defaultEntry)
  const payload = {}

  if (defaultEntry && typeof defaultEntry === 'object') {
    const startDate = normalizeValue(defaultEntry.startDate)
    const endDate = normalizeValue(defaultEntry.endDate)
    const preset = normalizeValue(defaultEntry.preset)
    const days = Number(defaultEntry.days)
    const months = Number(defaultEntry.months)

    if (startDate) payload.startDate = startDate
    if (endDate) payload.endDate = endDate
    if (preset) payload.preset = preset
    if (Number.isFinite(days) && days > 0) payload.days = days
    if (Number.isFinite(months) && months > 0) payload.months = months
  }

  if (value) {
    payload.value = value
  }

  return {
    value,
    rawValue: value,
    rawType: 'string',
    payload,
    sourceChartId: `interaction.defaults:${filterId}`,
    sourceChartType: 'interaction.defaults',
    sourceWorksheetName: worksheetName,
  }
}

function getEmitterVisualDefaultValue(emitter) {
  if (!emitter) return ''
  if (emitter.kind === 'dropdown') {
    return normalizeValue(emitter.defaultValue)
  }
  if (emitter.kind === 'input') {
    return normalizeValue(emitter.defaultValue)
  }
  if (emitter.kind === 'date-preset') {
    return normalizeValue(emitter.defaultPresetValue)
  }
  if (emitter.kind === 'date-range') {
    const startDate = normalizeValue(emitter.defaultStartValue)
    const endDate = normalizeValue(emitter.defaultEndValue)
    return startDate && endDate ? `${startDate}|${endDate}` : ''
  }
  return ''
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const chartsResponse = await post('/get_charts', {
    uri: args.uri,
    worksheet_name: args.worksheet,
  })
  const charts = Array.isArray(chartsResponse.charts) ? chartsResponse.charts : []
  const filteredCharts =
    args.chartIds.length > 0
      ? charts.filter((chart) => args.chartIds.includes(chart.chart_id))
      : charts

  const emitters = charts.flatMap((chart) => getWidgetEmitters(chart))
  const emitterRowsCache = new Map()
  const updates = []
  const failures = []
  const warnings = []

  function scheduleSqlReset(chart, sql, reason) {
    const nextSql = normalizeSql(sql)
    const existingIndex = updates.findIndex((item) => item.chart.chart_id === chart.chart_id)
    const nextUpdate = {
      chart,
      overrides: { sql: nextSql },
      reason,
    }
    if (existingIndex >= 0) {
      updates[existingIndex] = nextUpdate
      return
    }
    updates.push(nextUpdate)
  }

  function findMatchingEmitters(receiveConfig) {
    return emitters.filter((emitter) => {
      if (normalizeValue(emitter.event) !== normalizeValue(receiveConfig.event)) return false
      if (receiveConfig.name && normalizeValue(emitter.name) !== normalizeValue(receiveConfig.name)) return false
      if (receiveConfig.key && emitter.key && normalizeValue(emitter.key) !== normalizeValue(receiveConfig.key)) return false
      return true
    })
  }

  async function getEmitterRows(emitter) {
    if (!emitterRowsCache.has(emitter.chartId)) {
      emitterRowsCache.set(
        emitter.chartId,
        fetchSqlRows(args.uri, normalizeSql(emitter.sourceChart.sql)).catch((error) => {
          emitterRowsCache.delete(emitter.chartId)
          throw error
        }),
      )
    }
    return await emitterRowsCache.get(emitter.chartId)
  }

  async function getEmitterSamples(emitter, options = {}) {
    const preferredValue = normalizeValue(options.preferredValue)
    const mode = normalizeValue(options.mode) || 'runtime'

    if (emitter.kind === 'input') {
      const sampleValue = preferredValue || normalizeValue(emitter.defaultValue)
      if (!sampleValue) return []
      return [
        {
          value: sampleValue,
          rawValue: sampleValue,
          rawType: 'string',
          payload: {
            value: sampleValue,
          },
          sourceChartId: emitter.chartId,
          sourceChartType: emitter.sourceChart.type,
          sourceWorksheetName: emitter.sourceChart.worksheet_name,
        },
      ]
    }

    const rows = await getEmitterRows(emitter)

    if (emitter.kind === 'date-preset' || emitter.kind === 'date-range') {
      const firstRow = rows[0] || {}
      const endValue =
        normalizeValue(firstRow?.[emitter.endField || emitter.valueField]) ||
        normalizeValue(firstRow?.[emitter.valueField]) ||
        normalizeValue(emitter.defaultEndValue)
      if (!endValue) return []
      const preferredRangeMatch = preferredValue.match(
        /^(\d{4}-\d{2}-\d{2})\|(\d{4}-\d{2}-\d{2})$/,
      )
      const preferredPreset =
        emitter.presetOptions.find(
          (item) => normalizeValue(item.value) === preferredValue,
        ) || null
      const preset =
        preferredPreset ||
        emitter.presetOptions.find(
          (item) =>
            normalizeValue(item.value) === normalizeValue(emitter.defaultPresetValue),
        ) ||
        emitter.presetOptions.find((item) => normalizeValue(item.value))
      if (
        mode === 'default' &&
        emitter.kind === 'date-preset' &&
        preferredValue &&
        !preferredRangeMatch
      ) {
        return [
          {
            value: preferredValue,
            rawValue: preferredValue,
            rawType: 'string',
            payload: {
              value: preferredValue,
              preset: normalizeValue(preset?.value) || preferredValue,
              ...(Number(preset?.days) > 0 ? { days: Number(preset.days) } : {}),
              ...(Number(preset?.months) > 0 ? { months: Number(preset.months) } : {}),
            },
            sourceChartId: emitter.chartId,
            sourceChartType: emitter.sourceChart.type,
            sourceWorksheetName: emitter.sourceChart.worksheet_name,
          },
        ]
      }
      const rangeStartValue = preferredRangeMatch?.[1] || ''
      const rangeEndValue = preferredRangeMatch?.[2] || ''
      const startValue =
        rangeStartValue ||
        normalizeValue(firstRow?.[emitter.startField]) ||
        normalizeValue(emitter.defaultStartValue) ||
        ((emitter.kind === 'date-preset' && preset)
          ? shiftIsoDate(endValue, {
              days: Number(preset.days) || undefined,
              months: Number(preset.months) || undefined,
            })
          : endValue)
      const finalEndValue = rangeEndValue || endValue
      const sampleValue =
        preferredValue ||
        `${startValue}|${finalEndValue}`
      return [
        {
          value: sampleValue,
          rawValue: finalEndValue,
          rawType: 'string',
          payload: {
            value: sampleValue,
            preset: normalizeValue(preset?.value) || 'custom',
            startDate: startValue,
            endDate: finalEndValue,
            ...(Number(preset?.days) > 0 ? { days: Number(preset.days) } : {}),
            ...(Number(preset?.months) > 0 ? { months: Number(preset.months) } : {}),
          },
          sourceChartId: emitter.chartId,
          sourceChartType: emitter.sourceChart.type,
          sourceWorksheetName: emitter.sourceChart.worksheet_name,
        },
      ]
    }

    const values = []
    const seen = new Set()

    if (preferredValue) {
      const preferredRow = rows.find(
        (row) => normalizeValue(row?.[emitter.valueField]) === preferredValue,
      )
      const preferredRaw = preferredRow?.[emitter.valueField] ?? preferredValue
      values.push({
        value: preferredValue,
        rawValue: preferredRaw,
        rawType:
          typeof preferredRaw === 'number' && Number.isFinite(preferredRaw)
            ? 'number'
            : typeof preferredRaw,
        sourceChartId: emitter.chartId,
        sourceChartType: emitter.sourceChart.type,
        sourceWorksheetName: emitter.sourceChart.worksheet_name,
      })
      seen.add(preferredValue)
      if (options.limit === 1) {
        return values
      }
    }

    for (const row of rows) {
      const raw = row?.[emitter.valueField]
      const value = normalizeValue(raw)
      if (!value) continue
      if (emitter.emptyWhen.includes(value)) continue
      if (seen.has(value)) continue
      seen.add(value)
      values.push({
        value,
        rawValue: raw,
        rawType:
          typeof raw === 'number' && Number.isFinite(raw) ? 'number' : typeof raw,
        sourceChartId: emitter.chartId,
        sourceChartType: emitter.sourceChart.type,
        sourceWorksheetName: emitter.sourceChart.worksheet_name,
      })
      if (values.length >= (options.limit || args.sampleLimit)) break
    }
    return values
  }

  for (const chart of filteredCharts) {
    const interaction = chart?.spec?.interaction
    const receiveConfigs = Array.isArray(interaction?.receive) ? interaction.receive : []
    if (!receiveConfigs.length) continue
    const interactionDefaults =
      interaction?.defaults && typeof interaction.defaults === 'object'
        ? interaction.defaults
        : {}

    const currentSql = normalizeSql(chart.sql)
    const baseSql = normalizeSql(interaction?.baseSql) || currentSql
    const baselineSql = stripInteractionPlaceholders(baseSql)

    console.log(`\n[chart] ${chart.chart_id} ${chart.title || ''}`.trim())
    console.log(`  current.sql: ${currentSql}`)
    console.log(`  baseSql: ${baseSql}`)
    console.log(`  baseline.sql: ${baselineSql}`)

    await compileSql(args.uri, currentSql)
    await compileSql(args.uri, baselineSql)

    const receiveSamples = new Map()
    const defaultRuntimeEvents = new Map()
    let hasAnyDefaultScenario = false

    for (const receiveConfig of receiveConfigs) {
      const filterId = getFilterId(receiveConfig)
      const matchingEmitters = findMatchingEmitters(receiveConfig)
      const emitter = matchingEmitters[0]
      const widgetDefaultValue = getEmitterVisualDefaultValue(emitter)
      const interactionDefaultEntry = getInteractionDefaultEntry(interactionDefaults, filterId)
      const interactionDefaultValue = getInteractionDefaultValue(interactionDefaultEntry)

      if (widgetDefaultValue && !interactionDefaultValue) {
        const message =
          `${chart.chart_id} ${filterId} has widget default ${JSON.stringify(widgetDefaultValue)} ` +
          'but spec.interaction.defaults is missing it'
        warnings.push(message)
        console.log(`  warning: ${message}`)
      }

      if (widgetDefaultValue && interactionDefaultValue && widgetDefaultValue !== interactionDefaultValue) {
        const message =
          `${chart.chart_id} ${filterId} widget default ${JSON.stringify(widgetDefaultValue)} ` +
          `does not match spec.interaction.defaults ${JSON.stringify(interactionDefaultValue)}`
        warnings.push(message)
        console.log(`  warning: ${message}`)
      }

      const effectiveDefaultValue = widgetDefaultValue || interactionDefaultValue
      if (effectiveDefaultValue) {
        let defaultSample = null
        if (emitter) {
          const defaultSamples = await getEmitterSamples(emitter, {
            preferredValue: effectiveDefaultValue,
            limit: 1,
            mode: 'default',
          })
          defaultSample = defaultSamples[0] || null
        }
        if (!defaultSample && interactionDefaultValue) {
          defaultSample = buildInteractionDefaultSample(
            interactionDefaultEntry,
            args.worksheet,
            filterId,
          )
        }
        if (defaultSample?.value) {
          defaultRuntimeEvents.set(filterId, createRuntimeEvent(defaultSample, receiveConfig))
          hasAnyDefaultScenario = true
          console.log(
            `  default: ${filterId} -> ${JSON.stringify(defaultSample.value)}`,
          )
        }
      }

      if (args.filters.has(filterId)) {
        receiveSamples.set(filterId, [
          {
            value: args.filters.get(filterId),
            sourceChartId: 'manual',
            sourceChartType: 'manual',
            sourceWorksheetName: args.worksheet,
          },
        ])
        continue
      }

      if (!matchingEmitters.length) {
        const message = `no emitter samples found for receive config ${chart.chart_id}:${filterId}`
        warnings.push(message)
        console.log(`  warning: ${message}`)
        continue
      }

      const values = await getEmitterSamples(emitter)
      if (!values.length) {
        const message = `emitter ${emitter.chartId} returned no sample values for ${filterId}`
        warnings.push(message)
        console.log(`  warning: ${message}`)
        continue
      }

      receiveSamples.set(
        filterId,
        values,
      )
      console.log(
        `  samples: ${filterId} <- ${emitter.chartId} ${JSON.stringify(values.map((item) => item.value))}`,
      )
    }

    const scenarios = []
    const expectedDefaultSql = hasAnyDefaultScenario
      ? rebuildSqlFromScenario(chart, receiveConfigs, defaultRuntimeEvents)
      : baselineSql

    if (hasAnyDefaultScenario) {
      scenarios.push({
        name: 'default-state',
        runtimeEvents: defaultRuntimeEvents,
      })
    }

    if (currentSql !== expectedDefaultSql) {
      const message = hasAnyDefaultScenario
        ? `outer sql does not match resolved default-state sql: ${chart.chart_id}`
        : `outer sql differs from stripped baseSql: ${chart.chart_id}`
      warnings.push(message)
      console.log(`  warning: ${message}`)
      console.log(`  expected.default.sql: ${expectedDefaultSql}`)
      if (args.fixResetOuterSql) {
        scheduleSqlReset(
          chart,
          expectedDefaultSql,
          hasAnyDefaultScenario
            ? 'reset outer sql to resolved default-state sql'
            : 'reset outer sql to stripped baseSql',
        )
      }
    } else if (hasAnyDefaultScenario && currentSql !== baselineSql) {
      console.log('  info: outer sql matches resolved default-state sql')
    }

    for (const receiveConfig of receiveConfigs) {
      const filterId = getFilterId(receiveConfig)
      const samples = receiveSamples.get(filterId)
      if (!samples?.length) continue
      const runtimeEvents = new Map()
      runtimeEvents.set(filterId, createRuntimeEvent(samples[0], receiveConfig))
      scenarios.push({
        name: `single:${filterId}`,
        runtimeEvents,
      })
    }

    if (receiveConfigs.length > 1) {
      const runtimeEvents = new Map()
      let allPresent = true
      for (const receiveConfig of receiveConfigs) {
        const filterId = getFilterId(receiveConfig)
        const samples = receiveSamples.get(filterId)
        if (!samples?.length) {
          allPresent = false
          break
        }
        runtimeEvents.set(filterId, createRuntimeEvent(samples[0], receiveConfig))
      }
      if (allPresent) {
        scenarios.push({
          name: 'combined:first-values',
          runtimeEvents,
        })
      }
    }

    for (const scenario of scenarios) {
      const nextSql = rebuildSqlFromScenario(chart, receiveConfigs, scenario.runtimeEvents)
      try {
        await compileSql(args.uri, nextSql)
        if (args.verifyFormula) {
          await verifyFormula(args.uri, nextSql)
        }
        for (const [filterId, runtimeEvent] of scenario.runtimeEvents.entries()) {
          const sampleSet = receiveSamples.get(filterId) || []
          const sample = sampleSet.find((item) => item.value === runtimeEvent.value)
          if (!sample) continue
          if (sample.rawType === 'number' && nextSql.includes(`'${String(sample.rawValue)}'`)) {
            const message =
              `${chart.chart_id} ${scenario.name} quotes numeric filter value ${sample.rawValue}; ` +
              'this often returns 0 rows for numeric sheet columns'
            warnings.push(message)
            console.log(`  warning: ${message}`)
          }
        }
        console.log(`  ok: ${scenario.name}`)
        console.log(`    ${nextSql}`)
      } catch (error) {
        const message = `${chart.chart_id} ${scenario.name} failed: ${error.message}`
        failures.push(message)
        console.log(`  error: ${message}`)
      }
    }
  }

  if (args.fixResetOuterSql && updates.length) {
    for (const update of updates) {
      await setChart(args.uri, args.worksheet, update.chart, update.overrides)
      console.log(`\n[patched] ${update.chart.chart_id} ${update.reason}`)
    }
  }

  console.log('\n[summary]')
  console.log(`  charts scanned: ${filteredCharts.length}`)
  console.log(`  warnings: ${warnings.length}`)
  console.log(`  failures: ${failures.length}`)
  console.log(`  updates: ${updates.length}`)

  if (failures.length) {
    process.exitCode = 1
  }
}

main().catch((error) => {
  console.error(error.message || String(error))
  process.exit(1)
})
