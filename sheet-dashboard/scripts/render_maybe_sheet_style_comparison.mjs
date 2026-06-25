#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE_URL = 'https://a-play-be.maybeai.cn/api/v1/excel';
const CELL_WIDTH_PX = 101;
const CELL_HEIGHT_PX = 27;
const DASHBOARD_FROM_COL = 1; // B
const LEFT_TO_COL = 7; // G exclusive
const RIGHT_FROM_COL = 7; // H
const RIGHT_TO_COL = 13; // M exclusive
const ROW_SPAN = 12;
const ROW_GAP = 1;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillDir = path.resolve(__dirname, '..');
const defaultReportPath = path.join(skillDir, 'dist', 'maybe-sheet-style-comparison.report.json');
const defaultPayloadPath = path.join(skillDir, 'dist', 'maybe-sheet-style-comparison.payloads.json');

const cases = [
  {
    id: 'ecommerce-conversion-warm',
    title: 'E-commerce Conversion Warm',
    industry: 'ecommerce-analysis',
    variant: 'conversion-warm',
    story: 'funnel-diagnosis',
    layout: 'funnel-stack',
    ppt: 'data-dashboard',
    infographic: 'corporate-memphis',
    intent: 'Warm commercial scanning for traffic, GMV, and conversion breaks.',
    theme: {
      bg: '#FCFAF6',
      surface: '#FFFDF9',
      border: '#E8E0D4',
      title: '#231815',
      text: '#51463F',
      muted: '#8B7E74',
      grid: '#EEE6DB',
      accent: '#E66A3D',
      accent2: '#D9A441',
      accent3: '#5B8C7E',
      good: '#2F8F6B',
      bad: '#C75146',
      font: 'Plus Jakarta Sans',
      displayFont: 'Plus Jakarta Sans',
      lineType: 'solid',
      gridType: 'solid',
      symbol: 'circle',
      areaOpacity: 0.1,
      titleWeight: 700,
    },
    values: [22, 29, 35, 41, 47, 56, 61, 68, 74, 80, 86, 95],
  },
  {
    id: 'ecommerce-handwritten-review-board',
    title: 'E-commerce Handwritten Review Board',
    industry: 'ecommerce-analysis',
    variant: 'handwritten-review-board',
    story: 'performance-review',
    layout: 'kpi-plus-comparison',
    ppt: 'handwritten',
    infographic: 'craft-handmade',
    intent: 'Warm handwritten recap with note-board KPIs and marker-like trend rhythm.',
    theme: {
      bg: '#F7F0E4',
      surface: '#FFF8EE',
      border: '#D9C8B4',
      title: '#3D2B1F',
      text: '#5B4636',
      muted: '#8A7566',
      grid: '#E6D8C8',
      accent: '#D97706',
      accent2: '#4D7C0F',
      accent3: '#0F766E',
      good: '#4A9C6A',
      bad: '#B45309',
      font: 'Patrick Hand, Plus Jakarta Sans, sans-serif',
      displayFont: 'Patrick Hand',
      lineType: 'dashed',
      gridType: 'dashed',
      symbol: 'roundRect',
      areaOpacity: 0.14,
      titleWeight: 600,
    },
    values: [20, 25, 34, 39, 46, 58, 63, 70, 78, 83, 90, 99],
  },
  {
    id: 'ecommerce-sticky-notes-workshop',
    title: 'E-commerce Sticky Notes Workshop',
    industry: 'ecommerce-analysis',
    variant: 'sticky-notes-workshop',
    story: 'performance-review',
    layout: 'kpi-plus-comparison',
    ppt: 'sticky-notes',
    infographic: 'craft-handmade',
    intent: 'Brighter note clusters for workshop recap and grouped action framing.',
    theme: {
      bg: '#FFF8E8',
      surface: '#FFFDF6',
      border: '#E7D7B8',
      title: '#4A3426',
      text: '#5B4636',
      muted: '#907761',
      grid: '#F1E4C8',
      accent: '#F59E0B',
      accent2: '#84CC16',
      accent3: '#38BDF8',
      good: '#A78BFA',
      bad: '#FB7185',
      font: 'Plus Jakarta Sans',
      displayFont: 'Plus Jakarta Sans',
      lineType: 'solid',
      gridType: 'dashed',
      symbol: 'diamond',
      areaOpacity: 0.16,
      titleWeight: 700,
    },
    values: [17, 24, 33, 44, 49, 57, 69, 75, 83, 88, 98, 112],
  },
  {
    id: 'operations-control-room',
    title: 'Operations Control Room',
    industry: 'operations-analysis',
    variant: 'control-room',
    story: 'operations-monitor',
    layout: 'control-room-grid',
    ppt: 'executive-dark',
    infographic: 'technical-schematic',
    intent: 'Dense scan pattern for SLA, queues, exceptions, and alert states.',
    theme: {
      bg: '#0E1520',
      surface: '#131D2B',
      border: '#223245',
      title: '#E8EEF5',
      text: '#C8D2DE',
      muted: '#8FA0B5',
      grid: '#233446',
      accent: '#4FA3FF',
      accent2: '#F7B955',
      accent3: '#5ED0A5',
      good: '#4FD18B',
      bad: '#FF6B6B',
      font: 'JetBrains Mono',
      displayFont: 'JetBrains Mono',
      lineType: 'solid',
      gridType: 'solid',
      symbol: 'circle',
      areaOpacity: 0.1,
      titleWeight: 700,
    },
    values: [64, 67, 65, 71, 74, 79, 76, 82, 85, 84, 89, 93],
  },
  {
    id: 'operations-chalkboard-review',
    title: 'Operations Chalkboard Review',
    industry: 'operations-analysis',
    variant: 'chalkboard-review',
    story: 'operations-monitor',
    layout: 'control-room-grid',
    ppt: 'chalk-garden',
    infographic: 'chalkboard',
    intent: 'Dark chalkboard explainer with dashed guides and softer classroom energy.',
    theme: {
      bg: '#16171C',
      surface: '#1E1E24',
      border: '#3F3F46',
      title: '#F4F4F5',
      text: '#E4E4E7',
      muted: '#A1A1AA',
      grid: '#52525B',
      accent: '#FACC15',
      accent2: '#7DD3FC',
      accent3: '#86EFAC',
      good: '#C4B5FD',
      bad: '#FDA4AF',
      font: 'Patrick Hand, IBM Plex Sans, sans-serif',
      displayFont: 'Patrick Hand',
      lineType: 'dashed',
      gridType: 'dashed',
      symbol: 'rect',
      areaOpacity: 0.08,
      titleWeight: 600,
    },
    values: [58, 62, 66, 63, 71, 77, 79, 81, 88, 86, 92, 97],
  },
  {
    id: 'sales-quota-focus',
    title: 'Sales Quota Focus',
    industry: 'sales-analysis',
    variant: 'quota-focus',
    story: 'leaderboard-review',
    layout: 'leaderboard-grid',
    ppt: 'consulting-blue',
    infographic: 'corporate-memphis',
    intent: 'Target-forward sales performance with rankings and attainment markers.',
    theme: {
      bg: '#F8FAFC',
      surface: '#FFFFFF',
      border: '#DCE4EC',
      title: '#14202B',
      text: '#334155',
      muted: '#708090',
      grid: '#E8EEF4',
      accent: '#2563EB',
      accent2: '#0F9D7A',
      accent3: '#F59E0B',
      good: '#2E8B57',
      bad: '#D9534F',
      font: 'Aptos',
      displayFont: 'Aptos',
      lineType: 'solid',
      gridType: 'solid',
      symbol: 'circle',
      areaOpacity: 0.1,
      titleWeight: 700,
    },
    values: [40, 45, 48, 55, 59, 64, 69, 72, 78, 84, 88, 96],
  },
  {
    id: 'sales-cartoon-playbook',
    title: 'Sales Cartoon Playbook',
    industry: 'sales-analysis',
    variant: 'cartoon-playbook',
    story: 'leaderboard-review',
    layout: 'leaderboard-grid',
    ppt: 'cartoon',
    infographic: 'storybook-watercolor',
    intent: 'Friendlier teaching-style sales recap with brighter internal-sharing accents.',
    theme: {
      bg: '#FFF8F8',
      surface: '#FFFFFF',
      border: '#F0DDE7',
      title: '#3B2C35',
      text: '#5B4A57',
      muted: '#8B7A87',
      grid: '#F7E8EF',
      accent: '#FB7185',
      accent2: '#60A5FA',
      accent3: '#FBBF24',
      good: '#34D399',
      bad: '#A78BFA',
      font: 'Plus Jakarta Sans',
      displayFont: 'Plus Jakarta Sans',
      lineType: 'solid',
      gridType: 'dashed',
      symbol: 'diamond',
      areaOpacity: 0.14,
      titleWeight: 700,
    },
    values: [34, 39, 46, 54, 59, 66, 71, 80, 87, 93, 101, 108],
  },
];

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function usage() {
  console.error(`Usage:
  node scripts/render_maybe_sheet_style_comparison.mjs --uri <maybe_sheet_uri> [options]

Options:
  --worksheet <name>       Preferred worksheet name. Default: Style_Compare_<suffix>
  --out <path>             Report JSON path. Default: dist/maybe-sheet-style-comparison.report.json
  --payload-out <path>     Dry-run payload JSON path. Default: dist/maybe-sheet-style-comparison.payloads.json
  --dry-run                Build payloads without calling Maybe Sheet APIs.
  --base-url <url>         API base URL. Default: ${BASE_URL}
`);
}

function parseArgs(argv) {
  const args = {
    baseUrl: BASE_URL,
    out: defaultReportPath,
    payloadOut: defaultPayloadPath,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    switch (token) {
      case '--uri':
        args.uri = argv[index + 1];
        index += 1;
        break;
      case '--worksheet':
        args.worksheet = argv[index + 1];
        index += 1;
        break;
      case '--out':
        args.out = path.resolve(argv[index + 1]);
        index += 1;
        break;
      case '--payload-out':
        args.payloadOut = path.resolve(argv[index + 1]);
        index += 1;
        break;
      case '--base-url':
        args.baseUrl = String(argv[index + 1] || '').replace(/\/$/, '');
        index += 1;
        break;
      case '--dry-run':
        args.dryRun = true;
        break;
      case '--help':
      case '-h':
        usage();
        process.exit(0);
        break;
      default:
        throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!args.uri) {
    usage();
    throw new Error('--uri is required');
  }
  return args;
}

function getToken() {
  const token = String(process.env.MAYBEAI_API_TOKEN || '').trim();
  if (!token) {
    throw new Error('MAYBEAI_API_TOKEN is not set');
  }
  return token;
}

function workbookUri(uri) {
  return String(uri || '').split('#')[0].split('?')[0];
}

async function post(args, apiPath, payload) {
  const response = await fetch(`${args.baseUrl}${apiPath}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`${apiPath} failed: ${response.status} ${response.statusText} ${body}`);
  }
  const data = await response.json();
  if (data && data.success === false) {
    throw new Error(`${apiPath} failed: ${JSON.stringify(data)}`);
  }
  return data;
}

function normalizeWorksheetName(value) {
  const cleaned = String(value || '')
    .replace(/[\[\]\:\*\?\/\\]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 31);
  return cleaned || `Style_Compare_${Date.now().toString(36)}`;
}

function uniqueWorksheetName(preferred, existingNames) {
  const base = normalizeWorksheetName(preferred || `Style_Compare_${Date.now().toString(36)}`);
  if (!existingNames.has(base)) return base;
  for (let index = 2; index < 100; index += 1) {
    const suffix = `_${index}`;
    const candidate = `${base.slice(0, 31 - suffix.length)}${suffix}`;
    if (!existingNames.has(candidate)) return candidate;
  }
  throw new Error(`Cannot derive unique worksheet name from ${base}`);
}

function walk(value, visit) {
  if (!value || typeof value !== 'object') return;
  visit(value);
  if (Array.isArray(value)) {
    value.forEach((item) => walk(item, visit));
    return;
  }
  Object.values(value).forEach((item) => walk(item, visit));
}

function extractWorksheets(response) {
  const worksheets = [];
  walk(response, (node) => {
    if (!node || typeof node !== 'object' || Array.isArray(node)) return;
    const name = node.worksheet_name || node.name || node.title || node.sheet_name;
    if (!name) return;
    worksheets.push({
      name: String(name),
      gid: node.gid ?? node.sheet_id ?? node.worksheet_id ?? node.id,
    });
  });
  const seen = new Set();
  return worksheets.filter((item) => {
    if (seen.has(item.name)) return false;
    seen.add(item.name);
    return true;
  });
}

function sqlLiteral(value) {
  return `'${String(value).replace(/'/g, "''")}'`;
}

function quotedIdentifier(value) {
  return `"${String(value).replace(/"/g, '""')}"`;
}

function columnIndexToLabel(index) {
  let value = index + 1;
  let label = '';
  while (value > 0) {
    const remainder = (value - 1) % 26;
    label = String.fromCharCode(65 + remainder) + label;
    value = Math.floor((value - 1) / 26);
  }
  return label;
}

function toA1(col, row) {
  return `${columnIndexToLabel(col)}${row + 1}`;
}

function layoutFor(index) {
  const rowBand = Math.floor(index / 2);
  const isRight = index % 2 === 1;
  const fromCol = isRight ? RIGHT_FROM_COL : DASHBOARD_FROM_COL;
  const toCol = isRight ? RIGHT_TO_COL : LEFT_TO_COL;
  const fromRow = 1 + rowBand * (ROW_SPAN + ROW_GAP);
  const toRow = fromRow + ROW_SPAN;
  return {
    cell: toA1(fromCol, fromRow),
    range: `${toA1(fromCol, fromRow)}:${toA1(toCol - 1, toRow - 1)}`,
    width: (toCol - fromCol) * CELL_WIDTH_PX,
    height: ROW_SPAN * CELL_HEIGHT_PX,
    format: {
      from: { col: fromCol, row: fromRow, col_off: 0, row_off: 0 },
      to: { col: toCol, row: toRow, col_off: 0, row_off: 0 },
      lock_aspect_ratio: true,
      offset_x: 0,
      offset_y: 0,
      scale_x: 1,
      scale_y: 1,
    },
  };
}

function dataValues() {
  const rows = [['style_id', 'month_index', 'month', 'metric', 'value']];
  for (const item of cases) {
    item.values.forEach((value, index) => {
      rows.push([item.id, String(index + 1), months[index], 'trend', String(value)]);
    });
  }
  return rows;
}

function styleSpec(item) {
  const theme = item.theme;
  return {
    style: {
      title: item.title,
      background: theme.bg,
      palette: [theme.accent, theme.accent2, theme.accent3, theme.good, theme.bad],
      fontFamily: theme.font,
      displayFontFamily: theme.displayFont || theme.font,
      titleColor: theme.title,
      titleFontSize: item.variant === 'handwritten-review-board' ? 19 : (item.industry === 'ecommerce-analysis' ? 18 : 17),
      titleFontWeight: theme.titleWeight || 700,
      textColor: theme.text,
      textFontSize: 12,
      subTextColor: theme.muted,
      axisColor: theme.border,
      axisLabelFontSize: 11,
      gridLineColor: theme.grid,
      legend: 'top',
      legendTextColor: theme.text,
      legendFontSize: 11,
      tooltipBackground: theme.surface,
      tooltipTextColor: theme.title,
      tooltipFontSize: 12,
      labelFontSize: 11,
      labelFontWeight: item.variant === 'campaign-energy' ? 700 : 500,
      smooth: true,
    },
    boxAdaptation: {
      showDataZoom: 'auto',
    },
  };
}

function echartsRenderer(item) {
  const theme = JSON.stringify(item.theme);
  const meta = JSON.stringify({
    story: item.story,
    layout: item.layout,
    ppt: item.ppt,
    infographic: item.infographic,
  });
  return `{ library: 'echarts', handler: (data) => {
    const theme = ${theme};
    const meta = ${meta};
    const rows = Array.isArray(data) ? data : [];
    const values = rows.map((row) => Number(row.value ?? row['value'] ?? 0));
    const months = rows.map((row) => String(row.month ?? row['month'] ?? ''));
    const latest = values.length ? values[values.length - 1] : 0;
    const first = values.length ? values[0] : 0;
    const delta = first ? ((latest - first) / first) * 100 : 0;
    return {
      backgroundColor: theme.bg,
      color: [theme.accent, theme.accent2, theme.accent3, theme.good, theme.bad],
      textStyle: { color: theme.text, fontFamily: theme.font },
      grid: { left: 38, right: 26, top: 112, bottom: 34 },
      tooltip: {
        trigger: 'axis',
        backgroundColor: theme.surface,
        borderColor: theme.border,
        textStyle: { color: theme.title, fontFamily: theme.font }
      },
      xAxis: {
        type: 'category',
        data: months,
        axisLine: { lineStyle: { color: theme.border } },
        axisTick: { show: false },
        axisLabel: { color: theme.muted, fontSize: 10 },
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: theme.grid, type: theme.gridType || 'solid' } },
        axisLabel: { color: theme.muted, fontSize: 10 },
      },
      graphic: {
        elements: [
          {
            type: 'text',
            left: 22,
            top: 16,
            style: {
              text: String(latest),
              fill: theme.title,
              fontSize: 34,
              fontWeight: theme.titleWeight || 800,
              fontFamily: theme.displayFont || theme.font,
            },
          },
          {
            type: 'text',
            left: 22,
            top: 58,
            style: {
              text: meta.story + ' / ' + meta.layout,
              fill: theme.muted,
              fontSize: 12,
              fontWeight: 600,
              fontFamily: theme.displayFont || theme.font,
            },
          },
          {
            type: 'text',
            right: 24,
            top: 22,
            style: {
              text: (delta >= 0 ? '+' : '') + delta.toFixed(1) + '%',
              fill: delta >= 0 ? theme.good : theme.bad,
              fontSize: 18,
              fontWeight: 800,
              fontFamily: theme.font,
            },
          },
          {
            type: 'text',
            right: 24,
            top: 52,
            style: {
              text: 'PPT ' + meta.ppt + ' | Info ' + meta.infographic,
              fill: theme.muted,
              fontSize: 10,
              fontWeight: 600,
              fontFamily: theme.displayFont || theme.font,
            },
          },
        ],
      },
      series: [
        {
          name: 'Trend',
          type: 'line',
          smooth: true,
          symbol: theme.symbol || 'circle',
          symbolSize: theme.symbol === 'roundRect' ? 10 : 8,
          areaStyle: { color: theme.accent, opacity: theme.areaOpacity || 0.10 },
          lineStyle: { width: theme.lineType === 'dashed' ? 3.6 : 3, color: theme.accent, type: theme.lineType || 'solid' },
          itemStyle: { color: theme.accent },
          data: values,
        },
      ],
    };
  } }`;
}

function chartPayload(item, worksheetName, index) {
  const layout = layoutFor(index);
  const sql = [
    'select "month", "value"',
    `from ${quotedIdentifier(worksheetName)}`,
    `where "style_id" = ${sqlLiteral(item.id)} and "metric" = 'trend'`,
    'order by "month_index" asc',
  ].join(' ');
  return {
    cell: layout.cell,
    chart: {
      chart_id: `style-compare-${item.id}`,
      type: 'json',
      title: item.title,
      width: layout.width,
      height: layout.height,
      sql,
      spec: styleSpec(item),
      html: echartsRenderer(item),
      legend: 'top',
      show_blanks: 'gap',
      industry: item.industry,
      style_variant: item.variant,
      style_source: 'maybe-sheet-self-test',
      format: layout.format,
    },
    layout,
  };
}

function buildPayloadPlan(uri, worksheetName) {
  const data = dataValues();
  const charts = cases.map((item, index) => chartPayload(item, worksheetName, index));
  return {
    worksheetName,
    writeWorksheet: {
      uri,
      worksheet_name: worksheetName,
    },
    writeData: {
      uri,
      worksheet_name: worksheetName,
      range_address: `P1:T${data.length}`,
      values: data,
    },
    compileSql: charts.map(({ chart }) => ({ uri, sql: chart.sql })),
    addCharts: charts.map(({ cell, chart }) => ({
      uri,
      worksheet_name: worksheetName,
      cell,
      chart,
    })),
    expected: {
      chart_count: charts.length,
      chart_ids: charts.map(({ chart }) => chart.chart_id),
      layouts: charts.map(({ chart, layout }) => ({
        chart_id: chart.chart_id,
        cell: layout.cell,
        range: layout.range,
      })),
    },
  };
}

function validateLocalPlan(plan) {
  const errors = [];
  const ids = new Set();
  for (const payload of plan.addCharts) {
    const id = payload.chart.chart_id;
    if (ids.has(id)) errors.push(`duplicate chart_id ${id}`);
    ids.add(id);
    if (!payload.chart.sql) errors.push(`${id} missing sql`);
    if (!payload.chart.spec?.style?.background) errors.push(`${id} missing spec.style.background`);
    if (!payload.chart.html.includes("library: 'echarts'")) errors.push(`${id} is not echarts json renderer`);
    const { from, to } = payload.chart.format || {};
    if (!from || !to) errors.push(`${id} missing format.from/to`);
    if (from?.col < 1 || to?.col > 14) errors.push(`${id} outside B:N`);
  }
  if (errors.length) throw new Error(errors.join('\n'));
}

async function runMaybeSheet(args, plan) {
  const created = await post(args, '/write_new_worksheet', plan.writeWorksheet);
  await post(args, '/update_range', plan.writeData);
  const compileResults = [];
  for (const compilePayload of plan.compileSql) {
    compileResults.push(await post(args, '/sql/compile', compilePayload));
  }
  const addResults = [];
  for (const addPayload of plan.addCharts) {
    addResults.push(await post(args, '/add_chart', addPayload));
  }
  const chartsResponse = await post(args, '/get_charts', {
    uri: plan.writeWorksheet.uri,
    worksheet_name: plan.worksheetName,
  });
  const actualCharts = Array.isArray(chartsResponse.charts) ? chartsResponse.charts : [];
  const actualIds = new Set(actualCharts.map((chart) => chart.chart_id));
  const missing = plan.expected.chart_ids.filter((id) => !actualIds.has(id));
  if (missing.length) {
    throw new Error(`Missing Maybe Sheet charts after add_chart: ${missing.join(', ')}`);
  }
  return {
    created,
    compile_count: compileResults.length,
    add_count: addResults.length,
    actual_chart_count: actualCharts.length,
    expected_chart_ids_present: plan.expected.chart_ids.length - missing.length,
    chart_ids: plan.expected.chart_ids,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const uri = workbookUri(args.uri);
  fs.mkdirSync(path.dirname(args.out), { recursive: true });
  fs.mkdirSync(path.dirname(args.payloadOut), { recursive: true });

  let existingNames = new Set();
  if (!args.dryRun) {
    const worksheetsResponse = await post(args, '/list_worksheets', { uri });
    existingNames = new Set(extractWorksheets(worksheetsResponse).map((sheet) => sheet.name));
  }

  const worksheetName = uniqueWorksheetName(args.worksheet, existingNames);
  const plan = buildPayloadPlan(uri, worksheetName);
  validateLocalPlan(plan);
  fs.writeFileSync(args.payloadOut, JSON.stringify(plan, null, 2), 'utf8');

  const report = {
    mode: args.dryRun ? 'dry-run' : 'maybe-sheet',
    uri,
    worksheet_name: worksheetName,
    viewer_url: `${uri}?worksheet=${encodeURIComponent(worksheetName)}`,
    data_range: plan.writeData.range_address,
    chart_count: plan.expected.chart_count,
    chart_ids: plan.expected.chart_ids,
    layout: 'two-column B:N grid, data table in P:T',
    payloads: args.payloadOut,
    checks: ['local-payload-shape', 'B:N-layout', 'sql-per-chart', 'echarts-json-renderer'],
  };

  if (!args.dryRun) {
    report.maybe_sheet_result = await runMaybeSheet(args, plan);
    report.checks.push('write_new_worksheet', 'update_range-data-table', 'sql-compile', 'add_chart', 'get_charts');
  }

  fs.writeFileSync(args.out, JSON.stringify(report, null, 2), 'utf8');
  console.log(`Wrote ${args.payloadOut}`);
  console.log(`Wrote ${args.out}`);
  if (!args.dryRun) {
    console.log(`Created Maybe Sheet worksheet: ${worksheetName}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
