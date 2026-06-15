---
name: assess-sheet-confidence
description: Assesses spreadsheet value confidence, freshness, and sanity, and emits confidence metadata or creates a worksheet-local confidence mirror with colored cells. Use when the user wants write-time sidecar confidence metadata, confidence grading, freshness warnings, outlier or unit review, or a source-confident style worksheet. This skill focuses on scoring and validation, not detailed provenance capture.
metadata:
  openclaw:
    requires:
      env:
        - MAYBEAI_API_TOKEN
    primaryEnv: MAYBEAI_API_TOKEN
---

# Assess Sheet Confidence

Use this skill when the goal is confidence assessment for spreadsheet values. It handles:

- confidence scoring
- freshness grading
- sanity checks such as unit, range, magnitude, and outlier review
- write-time sidecar metadata for MaybeAI product overlays
- worksheet-local confidence mirrors such as `<worksheet_name>-source-confident` as fallback

Primary dependency: use the `maybeai-sheet` skill and its existing read/write/style APIs. For MaybeAI product-created workbooks or worksheets, prefer `metadata_output=sidecar` and write confidence metadata to play-be after the workbook/worksheet write succeeds.

Product sidecar target:

- play-be base URL: `http://play-be.omnimcp.ai/`
- feature config collection: `sheet_provenance_feature_config`
- cell metadata collection: `sheet_cell_metadata`
- feature endpoint: `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
- metadata endpoint: `POST http://play-be.omnimcp.ai/api/v1/sheet/cell-metadata/batch-upsert`

Authentication:

- default external/authenticated mode: set `MAYBEAI_API_TOKEN` and send `Authorization: Bearer <MAYBEAI_API_TOKEN>`
- trusted Hermes/OpenClaw internal mode: send `X-Internal-Token`, `X-User-Id`, and optional `X-User-Email`
- metadata must be written as the sheet owner user; otherwise the frontend owner query will not see it

This skill is primarily a write-time assessment skill. Hermes/OpenClaw should score confidence from the same creation context used to write the workbook/worksheet, then persist the sidecar after the sheet write returns `doc_id` and `gid`. The frontend only renders or hides the overlay; it does not create or repair confidence metadata in the current plan.

Shared contract: read `context-contract.md` first. It defines the inputs, scoring fields, confidence mirror rules, and worksheet contract.

## Trigger

Trigger when the user asks any of these:

- show confidence level for sheet values
- color cells by confidence
- create or refresh `<worksheet_name>-source-confident`
- emit `metadata_output=sidecar` confidence rows for the product overlay
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
11. Default to `metadata_output=sidecar` when the caller is creating a MaybeAI workbook or worksheet for the product UI. In sidecar mode, do not create `<worksheet_name>-source-confident`, do not create `source-tracking`, do not modify workbook styles, and do not write helper cells.
12. Use standalone mirror mode only as a fallback when play-be metadata APIs are unavailable or the user explicitly asks for workbook-visible confidence coloring.
13. In sidecar mode, emit confidence as numeric `confidence_level` 1-5, not only text tiers. `1` is very low and `5` is very high.
14. In sidecar mode, after the worksheet/workbook write succeeds, call play-be cell metadata batch-upsert and `provenance-feature/upsert` with source confidence enabled. If either upsert fails, report partial completion.
15. In standalone mode, create or refresh `<worksheet_name>-source-confident` as a pure mirror plus confidence coloring only.
16. When useful in standalone mode, enrich `source-tracking` with confidence, freshness, and validation columns. Do not erase existing provenance columns.
17. If the write path coerces visible strings like percentages, currencies, or dates into raw numbers, reapply display formats so the mirror still looks like the source.
18. After writing, verify the chosen output target: sidecar row counts and feature config for sidecar mode, or read affected worksheets back for standalone mode.
19. If `track-sheet-sources` is also running in the same creation flow, merge provenance and confidence fields into the same `cell_metadata[]` objects and perform one batch-upsert when practical. Do not overwrite valid source fields with `unknown` during confidence-only scoring.

## Output Rules

- The workbook change plus sidecar metadata write is the main output in `metadata_output=sidecar` mode.
- The chat response should be short and operational:
  - audited scope
  - metadata output mode
  - created or updated worksheets, if standalone fallback was used
  - confidence legend labels only
  - counts by confidence tier
  - counts by freshness level
  - counts by validation status
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
