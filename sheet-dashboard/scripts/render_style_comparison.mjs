#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillDir = path.resolve(__dirname, '..');
const defaultOut = path.join(skillDir, 'dist', 'style-comparison.html');
const outIndex = process.argv.indexOf('--out');
const outPath = outIndex >= 0 && process.argv[outIndex + 1]
  ? path.resolve(process.argv[outIndex + 1])
  : defaultOut;
const reportPath = outPath.replace(/\.html$/i, '.report.json');

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
      soft: '#F5ECE1',
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
      bodyFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      displayFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      borderStyle: 'solid',
      gridDash: '0',
      lineDash: '0',
    },
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
      soft: '#F0E1CF',
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
      bodyFont: '"Patrick Hand", "Plus Jakarta Sans", sans-serif',
      displayFont: '"Patrick Hand", cursive',
      borderStyle: 'dashed',
      gridDash: '5 5',
      lineDash: '8 6',
    },
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
      soft: '#F7E9C7',
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
      bodyFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      displayFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      borderStyle: 'solid',
      gridDash: '5 5',
      lineDash: '0',
    },
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
      soft: '#19283A',
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
      bodyFont: '"JetBrains Mono", "IBM Plex Sans", monospace',
      displayFont: '"JetBrains Mono", monospace',
      borderStyle: 'solid',
      gridDash: '0',
      lineDash: '0',
    },
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
      soft: '#28282F',
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
      bodyFont: '"Patrick Hand", "IBM Plex Sans", sans-serif',
      displayFont: '"Patrick Hand", cursive',
      borderStyle: 'dashed',
      gridDash: '6 6',
      lineDash: '10 6',
    },
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
      soft: '#EEF5FB',
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
      bodyFont: 'Aptos, Avenir Next, sans-serif',
      displayFont: 'Aptos, Avenir Next, sans-serif',
      borderStyle: 'solid',
      gridDash: '0',
      lineDash: '0',
    },
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
      soft: '#FCEEF3',
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
      bodyFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      displayFont: 'Plus Jakarta Sans, Avenir Next, sans-serif',
      borderStyle: 'solid',
      gridDash: '4 5',
      lineDash: '0',
    },
  },
];

const trend = [28, 34, 31, 42, 46, 51, 48, 58, 62, 67, 72, 78];
const bars = [72, 54, 42, 37, 29];
const funnel = [100, 74, 52, 31];

function hexToRgb(hex) {
  const value = hex.replace('#', '');
  const parsed = Number.parseInt(value.length === 3
    ? value.split('').map((c) => c + c).join('')
    : value, 16);
  return [(parsed >> 16) & 255, (parsed >> 8) & 255, parsed & 255];
}

function luminance(hex) {
  return hexToRgb(hex).map((channel) => {
    const normalized = channel / 255;
    return normalized <= 0.03928
      ? normalized / 12.92
      : Math.pow((normalized + 0.055) / 1.055, 2.4);
  }).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
}

function contrast(a, b) {
  const first = luminance(a);
  const second = luminance(b);
  const lighter = Math.max(first, second);
  const darker = Math.min(first, second);
  return (lighter + 0.05) / (darker + 0.05);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function svgLine(theme) {
  const width = 300;
  const height = 96;
  const padding = 14;
  const min = Math.min(...trend);
  const max = Math.max(...trend);
  const points = trend.map((value, index) => {
    const x = padding + (index * (width - padding * 2)) / (trend.length - 1);
    const y = height - padding - ((value - min) * (height - padding * 2)) / (max - min);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  const area = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`;
  return `
    <svg viewBox="0 0 ${width} ${height}" aria-hidden="true">
      <line x1="${padding}" y1="20" x2="${width - padding}" y2="20" stroke="${theme.grid}" stroke-dasharray="${theme.gridDash || '0'}" />
      <line x1="${padding}" y1="48" x2="${width - padding}" y2="48" stroke="${theme.grid}" stroke-dasharray="${theme.gridDash || '0'}" />
      <line x1="${padding}" y1="76" x2="${width - padding}" y2="76" stroke="${theme.grid}" stroke-dasharray="${theme.gridDash || '0'}" />
      <polygon points="${area}" fill="${theme.accent}" opacity="0.10" />
      <polyline points="${points}" fill="none" stroke="${theme.accent}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="${theme.lineDash || '0'}" />
      <circle cx="${width - padding}" cy="20.5" r="4.5" fill="${theme.accent2}" />
    </svg>`;
}

function barList(theme) {
  return bars.map((value, index) => {
    const labels = ['North', 'East', 'Online', 'Direct', 'Partner'];
    const color = [theme.accent, theme.accent2, theme.accent3, theme.good, theme.bad][index];
    return `
      <div class="bar-row">
        <span>${labels[index]}</span>
        <div class="bar-track"><i style="width:${value}%; background:${color}"></i></div>
        <b>${value}%</b>
      </div>`;
  }).join('');
}

function funnelStack(theme) {
  return funnel.map((value, index) => {
    const labels = ['Visit', 'Engage', 'Cart', 'Order'];
    const colors = [theme.accent, theme.accent2, theme.accent3, theme.good];
    return `
      <div class="funnel-row" style="width:${value}%; background:${colors[index]}">
        <span>${labels[index]}</span><b>${value}</b>
      </div>`;
  }).join('');
}

function card(testCase) {
  const { theme } = testCase;
  const vars = Object.entries(theme).map(([key, value]) => `--${key}:${value}`).join(';');
  return `
    <article class="case-card" style="${vars}">
      <header class="case-header">
        <div>
          <p class="eyebrow">${escapeHtml(testCase.industry)} / ${escapeHtml(testCase.variant)}</p>
          <h2>${escapeHtml(testCase.title)}</h2>
        </div>
        <span class="style-chip">${escapeHtml(testCase.layout)}</span>
      </header>
      <p class="intent">${escapeHtml(testCase.intent)}</p>
      <section class="kpi-strip">
        <div><span>Revenue</span><strong>$1.28M</strong><em>+12.4%</em></div>
        <div><span>Margin</span><strong>38.2%</strong><em>+3.1 pt</em></div>
        <div><span>Risk</span><strong>14</strong><em class="warn">watch</em></div>
      </section>
      <section class="mock-chart">
        <div class="chart-title">
          <span>Primary Trend</span>
          <b>${escapeHtml(testCase.story)}</b>
        </div>
        ${svgLine(theme)}
      </section>
      <section class="split">
        <div class="panel">
          <div class="chart-title"><span>Ranking</span><b>Top 5</b></div>
          ${barList(theme)}
        </div>
        <div class="panel">
          <div class="chart-title"><span>Funnel</span><b>${escapeHtml(testCase.infographic)}</b></div>
          <div class="funnel">${funnelStack(theme)}</div>
        </div>
      </section>
      <footer class="case-footer">
        <span>PPT ref: ${escapeHtml(testCase.ppt)}</span>
        <span>Widget tone: ${escapeHtml(testCase.layout)}</span>
      </footer>
    </article>`;
}

function runChecks() {
  const errors = [];
  const ids = new Set();
  const signatures = new Set();
  for (const item of cases) {
    for (const key of ['id', 'title', 'industry', 'variant', 'story', 'layout', 'ppt', 'infographic', 'intent']) {
      if (!item[key]) errors.push(`${item.id || 'unknown'} missing ${key}`);
    }
    if (ids.has(item.id)) errors.push(`duplicate id ${item.id}`);
    ids.add(item.id);
    const signature = [item.theme.bg, item.theme.surface, item.theme.accent, item.theme.title].join('|');
    if (signatures.has(signature)) errors.push(`duplicate theme signature ${item.id}`);
    signatures.add(signature);
    const titleContrast = contrast(item.theme.title, item.theme.surface);
    const textContrast = contrast(item.theme.text, item.theme.surface);
    if (titleContrast < 4.5) errors.push(`${item.id} title contrast ${titleContrast.toFixed(2)} < 4.5`);
    if (textContrast < 3.0) errors.push(`${item.id} text contrast ${textContrast.toFixed(2)} < 3.0`);
  }
  if (errors.length) {
    throw new Error(errors.join('\n'));
  }
  return {
    case_count: cases.length,
    ids: cases.map((item) => item.id),
    checks: ['required-fields', 'unique-style-signatures', 'title-contrast', 'text-contrast'],
  };
}

function html() {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sheet Dashboard Style Comparison</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #ECEFF3;
      color: #16202A;
      font-family: Avenir Next, Trebuchet MS, Verdana, sans-serif;
    }
    main {
      width: min(1480px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 28px 0 36px;
    }
    .page-header {
      display: grid;
      grid-template-columns: 1.3fr 0.7fr;
      gap: 24px;
      align-items: end;
      margin-bottom: 22px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 34px;
      line-height: 1.05;
      font-weight: 800;
      letter-spacing: 0;
    }
    .lead {
      margin: 0;
      max-width: 820px;
      color: #4A5564;
      font-size: 15px;
      line-height: 1.6;
    }
    .test-badge {
      justify-self: end;
      border: 1px solid #CBD3DD;
      background: #FFFFFF;
      color: #2F3B4A;
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.45;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }
    .case-card {
      min-height: 566px;
      padding: 18px;
      border: 1px var(--borderStyle, solid) var(--border);
      border-radius: 8px;
      background: var(--bg);
      color: var(--text);
      box-shadow: 0 18px 44px rgba(18, 28, 38, 0.10);
      display: flex;
      flex-direction: column;
      gap: 14px;
      font-family: var(--bodyFont, Avenir Next, sans-serif);
    }
    .case-header {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: start;
    }
    .eyebrow {
      margin: 0 0 6px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .08em;
      font-weight: 800;
    }
    h2 {
      margin: 0;
      color: var(--title);
      font-size: 22px;
      line-height: 1.08;
      letter-spacing: 0;
      font-family: var(--displayFont, inherit);
    }
    .style-chip {
      max-width: 150px;
      border: 1px var(--borderStyle, solid) var(--border);
      background: var(--surface);
      color: var(--title);
      padding: 7px 9px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      white-space: normal;
      text-align: center;
    }
    .intent {
      min-height: 42px;
      margin: 0;
      color: var(--text);
      font-size: 13px;
      line-height: 1.5;
    }
    .kpi-strip {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 9px;
    }
    .kpi-strip div, .mock-chart, .panel {
      border: 1px var(--borderStyle, solid) var(--border);
      border-radius: 8px;
      background: var(--surface);
    }
    .kpi-strip div {
      min-height: 86px;
      padding: 11px;
    }
    .kpi-strip span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
    }
    .kpi-strip strong {
      display: block;
      color: var(--title);
      margin-top: 8px;
      font-size: 24px;
      line-height: 1;
      letter-spacing: 0;
      font-family: var(--displayFont, inherit);
    }
    .kpi-strip em {
      display: inline-block;
      margin-top: 8px;
      color: var(--good);
      font-size: 12px;
      font-style: normal;
      font-weight: 800;
    }
    .kpi-strip em.warn { color: var(--bad); }
    .mock-chart {
      padding: 12px;
    }
    .chart-title {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: baseline;
      margin-bottom: 8px;
    }
    .chart-title span {
      color: var(--title);
      font-size: 13px;
      font-weight: 800;
    }
    .chart-title b {
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: .06em;
      text-align: right;
    }
    svg { display: block; width: 100%; height: 112px; }
    .split {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 12px;
      flex: 1;
    }
    .panel {
      min-height: 166px;
      padding: 12px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: 52px 1fr 36px;
      gap: 8px;
      align-items: center;
      margin: 11px 0;
      font-size: 11px;
    }
    .bar-row span { color: var(--text); overflow: hidden; text-overflow: ellipsis; }
    .bar-row b { color: var(--muted); text-align: right; font-size: 11px; }
    .bar-track {
      height: 8px;
      border-radius: 99px;
      background: var(--soft);
      overflow: hidden;
    }
    .bar-track i {
      display: block;
      height: 100%;
      border-radius: inherit;
    }
    .funnel {
      display: flex;
      flex-direction: column;
      gap: 9px;
      align-items: center;
      padding-top: 3px;
    }
    .funnel-row {
      height: 25px;
      min-width: 52%;
      border-radius: 5px;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 9px;
      font-size: 10px;
      font-weight: 800;
    }
    .case-footer {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding-top: 10px;
      border-top: 1px var(--borderStyle, solid) var(--border);
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }
    @media (max-width: 1180px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 760px) {
      main { width: min(100vw - 24px, 560px); padding-top: 18px; }
      .page-header { grid-template-columns: 1fr; }
      .test-badge { justify-self: start; }
      .grid { grid-template-columns: 1fr; }
      .split { grid-template-columns: 1fr; }
      h1 { font-size: 28px; }
    }
  </style>
</head>
<body>
  <main>
    <header class="page-header">
      <div>
        <h1>Sheet Dashboard Style Comparison</h1>
        <p class="lead">A deterministic self-test preview for report-grade Maybe Sheet dashboard styles. Every tile uses the same mock data so palette, density, KPI hierarchy, widget tone, and report references are easy to compare.</p>
      </div>
      <div class="test-badge">
        Generated by <strong>scripts/render_style_comparison.mjs</strong><br>
        Checks: required fields, unique style signatures, basic contrast
      </div>
    </header>
    <section class="grid">
      ${cases.map(card).join('\n')}
    </section>
  </main>
</body>
</html>`;
}

const report = runChecks();
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, html(), 'utf8');
fs.writeFileSync(reportPath, JSON.stringify({ ...report, html: outPath }, null, 2), 'utf8');
console.log(`Wrote ${outPath}`);
console.log(`Wrote ${reportPath}`);
