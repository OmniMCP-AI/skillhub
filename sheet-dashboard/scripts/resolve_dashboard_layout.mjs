#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEFAULT_CELL_WIDTH_PX = 101;
const DEFAULT_CELL_HEIGHT_PX = 27;
const DEFAULT_FROM_COL = 1; // B
const DEFAULT_TO_COL = 14; // N inclusive as an exclusive boundary

function usage() {
  console.error(`Usage:
  node scripts/resolve_dashboard_layout.mjs --input <layout_or_pack.json> [options]

Options:
  --output <path>             Write resolved layout JSON to this path. Defaults to stdout.
  --cell-width-px <number>    Spreadsheet cell width. Default: ${DEFAULT_CELL_WIDTH_PX}
  --cell-height-px <number>   Spreadsheet cell height. Default: ${DEFAULT_CELL_HEIGHT_PX}
  --allow-outside-bounds      Warn instead of failing when a slot is outside B:N.
`);
}

function parseArgs(argv) {
  const args = {
    cellWidthPx: DEFAULT_CELL_WIDTH_PX,
    cellHeightPx: DEFAULT_CELL_HEIGHT_PX,
    allowOutsideBounds: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    switch (token) {
      case '--input':
        args.input = path.resolve(argv[index + 1]);
        index += 1;
        break;
      case '--output':
        args.output = path.resolve(argv[index + 1]);
        index += 1;
        break;
      case '--cell-width-px':
        args.cellWidthPx = Number(argv[index + 1]);
        index += 1;
        break;
      case '--cell-height-px':
        args.cellHeightPx = Number(argv[index + 1]);
        index += 1;
        break;
      case '--allow-outside-bounds':
        args.allowOutsideBounds = true;
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

  if (!args.input) {
    usage();
    throw new Error('--input is required');
  }
  if (!Number.isFinite(args.cellWidthPx) || args.cellWidthPx <= 0) {
    throw new Error('--cell-width-px must be a positive number');
  }
  if (!Number.isFinite(args.cellHeightPx) || args.cellHeightPx <= 0) {
    throw new Error('--cell-height-px must be a positive number');
  }
  return args;
}

function normalizeValue(value) {
  return String(value ?? '').trim();
}

function toFiniteNumber(value, fallback = 0) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : fallback;
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

function columnLabelToIndex(label) {
  let col = 0;
  for (const char of String(label || '').toUpperCase()) {
    if (char < 'A' || char > 'Z') throw new Error(`Invalid column label: ${label}`);
    col = col * 26 + (char.charCodeAt(0) - 64);
  }
  return col - 1;
}

function toA1(col, row) {
  return `${columnIndexToLabel(col)}${row + 1}`;
}

function parseCell(cell) {
  const match = normalizeValue(cell).match(/^([A-Za-z]+)(\d+)$/);
  if (!match) throw new Error(`Invalid A1 cell: ${cell}`);
  const rowNumber = Number(match[2]);
  if (!Number.isFinite(rowNumber) || rowNumber < 1) throw new Error(`Invalid A1 row: ${cell}`);
  return {
    col: columnLabelToIndex(match[1]),
    row: rowNumber - 1,
  };
}

function parseRange(range) {
  const parts = normalizeValue(range).split(':');
  if (parts.length !== 2) throw new Error(`Invalid A1 range: ${range}`);
  const from = parseCell(parts[0]);
  const toInclusive = parseCell(parts[1]);
  const to = {
    col: toInclusive.col + 1,
    row: toInclusive.row + 1,
  };
  if (to.col <= from.col || to.row <= from.row) throw new Error(`Invalid A1 range: ${range}`);
  return {
    fromCol: from.col,
    fromRow: from.row,
    toCol: to.col,
    toRow: to.row,
  };
}

function rangeLabel(rect) {
  return `${toA1(rect.fromCol, rect.fromRow)}:${toA1(rect.toCol - 1, rect.toRow - 1)}`;
}

function visualRect(rect, layout) {
  return {
    left: rect.fromCol * layout.cellWidthPx + layout.inner_padding.left_px,
    top: rect.fromRow * layout.cellHeightPx + layout.inner_padding.top_px,
    right: rect.fromCol * layout.cellWidthPx + layout.inner_padding.left_px + layout.width_px,
    bottom: rect.fromRow * layout.cellHeightPx + layout.inner_padding.top_px + layout.height_px,
  };
}

function rectsOverlap(left, right) {
  return !(
    left.right <= right.left ||
    right.right <= left.left ||
    left.bottom <= right.top ||
    right.bottom <= left.top
  );
}

function normalizePadding(value) {
  return {
    left_px: Math.max(0, toFiniteNumber(value?.left_px, 0)),
    right_px: Math.max(0, toFiniteNumber(value?.right_px, 0)),
    top_px: Math.max(0, toFiniteNumber(value?.top_px, 0)),
    bottom_px: Math.max(0, toFiniteNumber(value?.bottom_px, 0)),
  };
}

function findSlots(input) {
  if (Array.isArray(input)) return input;
  if (Array.isArray(input?.dashboard_style_pack?.layout_slots)) return input.dashboard_style_pack.layout_slots;
  if (Array.isArray(input?.layout_slots)) return input.layout_slots;
  if (Array.isArray(input?.dashboard_style_pack_candidate?.extracted_layout?.layout_slots)) {
    return input.dashboard_style_pack_candidate.extracted_layout.layout_slots;
  }
  if (Array.isArray(input?.dashboard_layout_config?.modules)) return input.dashboard_layout_config.modules;
  if (Array.isArray(input?.modules)) return input.modules;
  if (Array.isArray(input?.charts)) {
    return input.charts.map((chart) => ({
      slot_id: chart.chart_id || chart.id || chart.goal,
      role: chart.role || chart.chart_type,
      maybe_sheet_slot: chart.layout?.range || chart.range,
      inner_padding: chart.layout?.inner_padding,
    }));
  }
  throw new Error('Input must contain layout slots, dashboard_style_pack.layout_slots, dashboard_layout_config.modules, or charts[].layout.range');
}

function slotRange(slot) {
  return slot?.maybe_sheet_slot || slot?.slot || slot?.range || slot?.layout?.range;
}

function resolveSlot(slot, args) {
  const rawRange = slotRange(slot);
  if (!rawRange) throw new Error(`Missing slot range for ${slot.slot_id || slot.id || '(unnamed slot)'}`);
  const rect = parseRange(rawRange);
  const innerPadding = normalizePadding(slot.inner_padding || slot.layout?.inner_padding);
  const slotWidthPx = (rect.toCol - rect.fromCol) * args.cellWidthPx;
  const slotHeightPx = (rect.toRow - rect.fromRow) * args.cellHeightPx;
  const widthPx = slotWidthPx - innerPadding.left_px - innerPadding.right_px;
  const heightPx = slotHeightPx - innerPadding.top_px - innerPadding.bottom_px;
  if (widthPx <= 0 || heightPx <= 0) {
    throw new Error(`inner_padding is larger than slot ${rawRange}`);
  }

  const layout = {
    cell: toA1(rect.fromCol, rect.fromRow),
    range: rangeLabel(rect),
    column_span: rect.toCol - rect.fromCol,
    row_span: rect.toRow - rect.fromRow,
    slot_width_px: slotWidthPx,
    slot_height_px: slotHeightPx,
    width_px: widthPx,
    height_px: heightPx,
    cellWidthPx: args.cellWidthPx,
    cellHeightPx: args.cellHeightPx,
    inner_padding: innerPadding,
    format: {
      from: { col: rect.fromCol, row: rect.fromRow, col_off: 0, row_off: 0 },
      to: { col: rect.toCol, row: rect.toRow, col_off: 0, row_off: 0 },
      lock_aspect_ratio: true,
      offset_x: innerPadding.left_px,
      offset_y: innerPadding.top_px,
      scale_x: 1,
      scale_y: 1,
    },
  };

  return {
    ...slot,
    maybe_sheet_slot: rangeLabel(rect),
    resolved_layout: layout,
    chart_payload_layout: {
      cell: layout.cell,
      width: layout.width_px,
      height: layout.height_px,
      format: layout.format,
    },
    _rect: rect,
    _visualRect: visualRect(rect, layout),
  };
}

function validateResolved(resolved, args) {
  const warnings = [];
  const errors = [];
  for (const slot of resolved) {
    if (slot._rect.fromCol < DEFAULT_FROM_COL || slot._rect.toCol > DEFAULT_TO_COL) {
      const message = `${slot.slot_id || slot.id || slot.maybe_sheet_slot} is outside B:N`;
      if (args.allowOutsideBounds) warnings.push(message);
      else errors.push(message);
    }
  }
  for (let leftIndex = 0; leftIndex < resolved.length; leftIndex += 1) {
    for (let rightIndex = leftIndex + 1; rightIndex < resolved.length; rightIndex += 1) {
      const left = resolved[leftIndex];
      const right = resolved[rightIndex];
      if (rectsOverlap(left._visualRect, right._visualRect)) {
        errors.push(
          `${left.slot_id || left.id || left.maybe_sheet_slot} visual rect overlaps ${right.slot_id || right.id || right.maybe_sheet_slot}`,
        );
      }
    }
  }
  if (errors.length) throw new Error(errors.join('\n'));
  return warnings;
}

export function resolveDashboardLayout(input, options = {}) {
  const args = {
    cellWidthPx: toFiniteNumber(options.cellWidthPx, DEFAULT_CELL_WIDTH_PX),
    cellHeightPx: toFiniteNumber(options.cellHeightPx, DEFAULT_CELL_HEIGHT_PX),
    allowOutsideBounds: Boolean(options.allowOutsideBounds),
  };
  const slots = findSlots(input);
  const resolved = slots.map((slot) => resolveSlot(slot, args));
  const warnings = validateResolved(resolved, args);
  return {
    summary: {
      slots: resolved.length,
      cell_width_px: args.cellWidthPx,
      cell_height_px: args.cellHeightPx,
      warnings,
    },
    resolved_slots: resolved.map(({ _rect, _visualRect, ...slot }) => slot),
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = JSON.parse(fs.readFileSync(args.input, 'utf8'));
  const result = resolveDashboardLayout(input, args);
  const output = JSON.stringify(result, null, 2);
  if (args.output) {
    fs.mkdirSync(path.dirname(args.output), { recursive: true });
    fs.writeFileSync(args.output, `${output}\n`, 'utf8');
    console.log(`Wrote ${args.output}`);
  } else {
    console.log(output);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error.message || String(error));
    process.exit(1);
  });
}
