---
name: maybeai-formula-report
description: Builds a MaybeAI Sheet workbook where raw worksheets are stored as values and derived report worksheets are activated as live formulas, so edits to raw data automatically recalculate the report. Use when the user wants traceable spreadsheet lineage, formula-driven reports, "改 raw 自动重算", "公式可追溯", or one MaybeAI workbook containing both raw and report sheets.
version: 0.3.2
created: 2026-06-18
---

# maybeai-formula-report

This skill owns the workbook-level ETL and traceability pattern for MaybeAI Sheet:

- raw sheets are values
- report sheets are formulas
- totals stay as formulas such as `=SUM(B2:E2)`
- cross-sheet reuse stays as formulas
- the workbook is recalculated and verified before delivery

It does not decide business conclusions or report wording.

## Use when

Trigger this skill when the user wants most of these:

- output in MaybeAI Sheet
- one workbook containing both source tabs and final report tabs
- formula lineage, traceability, or automatic recalculation after raw edits
- a repeatable raw -> normalized -> report workflow

Examples:

- "把原始表和分析表放在同一个 MaybeAI workbook 里，分析区全部用公式引用"
- "不要写死全年值，全年列要是 SUM 公式"
- "raw 改了以后报告自动重算"

## Do not use when

- the task is generic MaybeAI Sheet CRUD with no lineage requirement
- the deliverable is local xlsx only
- the report can safely use pasted values instead of live formulas

Use `maybeai-sheet` for generic API mechanics. Use `traceable-financial-analysis` when the task needs the finance report contract and business narrative.

## Loading order

1. Read `references/boundaries.md` to confirm this skill is the right layer.
2. Read `references/maybe-sheet-api-notes.md` before writing or activating formulas.
3. If you need lower-level endpoint details or broader worksheet operations, switch to `maybeai-sheet` and read its `SKILL.md` plus `scripts/05-worksheets.sh`, `scripts/06-formulas.sh`, and `scripts/02-read-data.sh`.
4. For domain-specific row maps, report layouts, or finance semantics, switch to the domain skill instead of adding those details here.

## Workflow

1. Extract and normalize raw inputs into a stable worksheet schema.
2. Write raw worksheets first.
3. Create report worksheets with final shape and placeholders.
4. Activate report blocks with `formula/batch_set` whenever the formulas can be grouped into rectangles.
5. Use `formula/set` only for sparse one-off cells that are not worth batching.
6. Recalculate the workbook once near the end.
7. Read back representative cells to verify traceability.

## Hard rules

1. Raw worksheets are values only.
2. Derived report cells are formulas, not pasted numbers.
3. Yearly or total columns remain formulas such as `=SUM(B:E)`.
4. Cross-sheet KPI reuse must reference source cells by formula.
5. For report builds, prefer `formula/batch_set` over many repeated `formula/set` calls.
6. Delivery is not complete until recalculation and readback verification both pass.

## Reference map

- `references/boundaries.md`
  Decides whether a change belongs in `maybeai-sheet`, `maybeai-formula-report`, or `traceable-financial-analysis`.
- `references/maybe-sheet-api-notes.md`
  Low-freedom operational details for the external MaybeAI Sheet endpoints such as `write_new_worksheet`, `formula/batch_set`, `formula/set`, recalculation, and deletion edge cases.

## Scripts

- `scripts/common.sh`
  Shared helper for auth, URL construction, and JSON POST calls.
- `scripts/write_worksheet.sh`
  Creates one worksheet from a JSON 2D array. Use for raw sheets or report scaffolds.
- `scripts/set_formula_and_recalc.sh`
  Sets one persisted formula or one batch of rectangular formula blocks, then optionally recalculates the whole workbook.
- `scripts/verify_formula_cells.sh`
  Reads back one or more cells and fails if they are empty, still show literal `=...` text, or break simple expectations.

## Anti-patterns

- putting formulas into raw source tabs
- writing final report numbers as static values when they should be derived
- storing yearly columns as copied Q4 values instead of formulas
- skipping workbook recalculation
- skipping readback verification
