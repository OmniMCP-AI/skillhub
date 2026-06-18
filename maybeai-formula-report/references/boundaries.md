# Boundaries

Use this reference when deciding where a change belongs.

## The three-layer split

### 1. `maybeai-sheet`

Owns generic MaybeAI Sheet mechanics:

- upload, read, write, export
- worksheet creation and deletion
- `formula/set`
- `recalculate_formulas`
- formatting, filters, SQL sheet behaviors
- backend quirks that apply to any workbook

If a lesson would help a non-finance workbook, it belongs there.

Examples:

- `write_new_worksheet` needs `worksheet_name`
- avoid `None` in `values`
- `formula/set` needs a final recalculation
- `update_range` is unreliable for single-cell formula-like edits

### 2. `maybeai-formula-report`

Owns the traceable workbook workflow:

- raw -> normalized -> report sequencing
- values-in-raw, formulas-in-report architecture
- sheet build order
- formula activation order
- total-column rules such as `=SUM(B:E)`
- verification that formulas are live and traceable

If the rule is about workbook lineage or derived-sheet mechanics, it belongs here.

Examples:

- create raw sheets before derived sheets
- yearly columns must remain formulas
- cross-sheet KPI cells must reference source sheets, not copied values
- verify readback after recalculation

### 3. `traceable-financial-analysis`

Owns financial meaning and output contract:

- which sheets exist
- which metrics and rows must appear
- how management conclusions are phrased
- which ratios matter
- what counts as a complete boss-review report
- finance-specific QA and consistency rules

If the rule is about finance semantics rather than sheet mechanics, it belongs there.

Examples:

- use the 9-sheet boss-review structure
- distinguish single-quarter vs cumulative metrics
- row names such as 净利率, 资产负债率, OCF/净利润
- required narrative, risks, and next-step suggestions

## Fast decision rule

Ask one question:

"If I changed the business domain but still used MaybeAI Sheets, would this rule still be true?"

- yes -> `maybeai-sheet` or `maybeai-formula-report`
- no -> `traceable-financial-analysis`

Then ask:

"Is this about low-level API usage, or about workbook lineage/orchestration?"

- API usage -> `maybeai-sheet`
- lineage/orchestration -> `maybeai-formula-report`
