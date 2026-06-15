---
name: assess-sheet-confidence
description: Assesses spreadsheet value confidence, freshness, and sanity, and emits confidence metadata for MaybeAI Sheet overlays. Product mode writes play-be sidecar metadata only and does not create worksheet-local confidence mirrors. Use when the user wants write-time sidecar confidence metadata, confidence grading, freshness warnings, outlier or unit review. This skill focuses on scoring and validation, not detailed provenance capture.
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
- play-be sidecar confidence metadata for MaybeAI Sheet overlays

Primary dependency: use the `maybeai-sheet` skill and its existing read/write/style APIs. For MaybeAI product-created workbooks or worksheets, use `metadata_output=sidecar` and write confidence metadata to play-be after the workbook/worksheet write succeeds.

Product sidecar target:

- play-be base URL: `http://play-be.omnimcp.ai/`
- feature config collection: `sheet_provenance_feature_config`
- cell metadata collection: `sheet_cell_metadata`
- feature endpoint: `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
- metadata endpoint: `POST http://play-be.omnimcp.ai/api/v1/sheet/cell-metadata/batch-upsert`

Authentication:

- default external/authenticated mode: set `MAYBEAI_API_TOKEN` and send `Authorization: Bearer <MAYBEAI_API_TOKEN>`
- trusted Hermes/OpenClaw internal mode: send `X-Internal-Token`, `X-User-Id`, and optional `X-User-Email`
- access is still checked through document permissions, but sidecar metadata is shared by `doc_id + gid + cell`; `user_id` is audit/last-writer metadata, not the visibility boundary

This skill is primarily a write-time assessment skill. Hermes/OpenClaw should score confidence from the same creation context used to write the workbook/worksheet, then persist the sidecar after the sheet write returns `doc_id` and `gid`. The frontend only renders or hides the overlay; it does not create or repair confidence metadata in the current plan.

Product UI note:

- The product UI may expose one combined `Source/Confidence Tracking` control and one combined `Source/Confidence Overlay`.
- Keep this skill separate from `track-sheet-sources`: this skill owns confidence fields (`confidence_level`, `confidence_reason`, `freshness`, `validation`).
- The backend still stores separate feature flags (`source_tracking_enabled`, `source_confidence_enabled`) and separate metadata fields in the same `sheet_cell_metadata` row.

Product output target:

- For `maybe.ai/docs/spreadsheets/d/...`, materialize confidence as play-be sidecar metadata.
- Workbook-visible confidence mirrors are an offline export concern, not the product storage path.

Shared contract: read `context-contract.md` first. It defines the inputs, scoring fields, and sidecar metadata contract.

## Trigger

Trigger when the user asks any of these:

- show confidence level for sheet values
- color cells by confidence
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
4. Prefer existing play-be sidecar provenance from `sheet_cell_metadata` when available.
5. Treat workbook-visible `source-tracking` as legacy/offline evidence only. If sidecar provenance is absent, reconstruct the minimum evidence needed to score confidence, but do not attempt a full provenance audit unless the user explicitly asked for it.
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
11. Use `metadata_output=sidecar` when the caller is creating or updating a MaybeAI workbook or worksheet for the product UI.
12. Product UI display comes from play-be sidecar metadata. Workbook-visible confidence mirrors belong only to separately requested offline exports.
13. In sidecar mode, emit confidence as numeric `confidence_level` 1-5, not only text tiers. `1` is very low and `5` is very high.
14. In sidecar mode, after the worksheet/workbook write succeeds, call play-be cell metadata batch-upsert and `provenance-feature/upsert` with source confidence enabled. If either upsert fails, report partial completion.
15. After writing, verify sidecar row counts and feature config.
16. If `track-sheet-sources` is also running in the same creation flow, merge provenance and confidence fields into the same `cell_metadata[]` objects and perform one batch-upsert when practical. Do not overwrite valid source fields with `unknown` during confidence-only scoring.
17. Treat `doc_id + gid + row + col` as the identity key for sidecar cell metadata. Do not create user-specific duplicate rows for the same cell.

## Output Rules

- The workbook change plus sidecar metadata write is the main output in `metadata_output=sidecar` mode.
- The chat response should be short and operational:
  - audited scope
  - metadata output mode
  - play-be sidecar row count
  - confidence legend labels only
  - counts by confidence tier
  - counts by freshness level
  - counts by validation status
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
