---
name: assess-sheet-confidence
description: Assesses spreadsheet value confidence, freshness, and sanity, and creates or refreshes a worksheet-local confidence mirror with colored cells. Use when the user wants confidence grading, freshness warnings, outlier or unit review, or a source-confident style worksheet. This skill focuses on scoring and validation, not detailed provenance capture.
---

# Assess Sheet Confidence

Use this skill when the goal is confidence assessment for spreadsheet values. It handles:

- confidence scoring
- freshness grading
- sanity checks such as unit, range, magnitude, and outlier review
- worksheet-local confidence mirrors such as `<worksheet_name>-source-confident`

Primary dependency: use the `maybeai-sheet` skill and its existing read/write/style APIs.

Shared contract: read `context-contract.md` first. It defines the inputs, scoring fields, confidence mirror rules, and worksheet contract.

## Trigger

Trigger when the user asks any of these:

- show confidence level for sheet values
- color cells by confidence
- create or refresh `<worksheet_name>-source-confident`
- assess whether data is fresh or stale
- flag unreasonable units, impossible ranges, or suspicious magnitudes
- mark outliers for review
- reduce hallucination risk by showing confidence or uncertainty

Do not use this skill for:

- detailed provenance capture
- source-link collection
- paragraph or field-path tracking
- formula lineage

Use `track-sheet-sources` for provenance capture.
Use `analyze-sheet-lineage` for formula dependency tracing.

## What To Read

- Always read `context-contract.md`.
- Read `workflow.md` before writing or styling worksheets.
- Read `output-format.md` before producing the final answer.
- Read `verification.md` when you need live verification criteria.
- Read `source-taxonomy.md` when confidence depends on source quality or ambiguous source types.

## Execution Rules

1. Treat `spreadsheet_url` as required.
2. Prefer `selected_range` as the audit scope. If absent, audit the active worksheet's used range only when the user clearly asked for whole-sheet coverage.
3. Ignore blank cells, `N/A`, `NA`, `null`, `--`, or similar placeholders unless the cell itself is clearly an error value that should be tracked.
4. Prefer existing provenance from `source-tracking` when available.
5. If `source-tracking` is absent, reconstruct the minimum evidence needed to score confidence, but do not attempt a full provenance audit unless the user explicitly asked for it.
6. Score confidence with five tiers:
   - `very_high`
   - `high`
   - `medium`
   - `low`
   - `very_low`
7. Treat the color mapping as internal style only. Do not expose raw hex values in user-visible worksheet cells.
8. Track freshness separately from confidence:
   - prefer `effective_date`
   - otherwise `publish_date`
   - otherwise `modified_date`
   - otherwise `retrieved_at`
9. Run a lightweight sanity validation pass when helpful:
   - unit consistency
   - impossible ranges
   - magnitude issues
   - outlier review
10. Do not treat outliers as automatic errors. Mark them `needs_review` unless a stronger rule proves `invalid`.
11. Create or refresh `<worksheet_name>-source-confident` as a pure mirror plus confidence coloring only.
12. When useful, enrich `source-tracking` with confidence, freshness, and validation columns. Do not erase existing provenance columns.
13. If the write path coerces visible strings like percentages, currencies, or dates into raw numbers, reapply display formats so the mirror still looks like the source.
14. After writing, read the affected worksheets back and verify visible values, structure, and expected assessment fields.

## Output Rules

- The workbook change is the main output.
- The chat response should be short and operational:
  - audited scope
  - created or updated worksheets
  - confidence legend labels only
  - counts by confidence tier
  - counts by freshness level
  - counts by validation status
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
