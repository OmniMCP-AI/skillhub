---
name: track-sheet-sources
description: Tracks spreadsheet value provenance and writes source metadata with source type, links, section locators, evidence snippets, retrieval method, and source dates. Use when the user wants to know where sheet values came from, attach citations to cells, or emit write-time sidecar metadata for MaybeAI Sheet overlays. Product mode writes play-be sidecar metadata only and does not create source-tracking worksheets. This skill focuses on provenance, not confidence coloring.
metadata:
  openclaw:
    requires:
      env:
        - MAYBEAI_API_TOKEN
    primaryEnv: MAYBEAI_API_TOKEN
---

# Track Sheet Sources

Use this skill when the goal is source provenance for spreadsheet values. It is for OpenClaw, Hermes, or any AI assistant that can inspect execution context such as tool-call traces, session history, attached citations, uploaded files, and opened pages.

Primary dependency: use the `maybeai-sheet` skill and its existing worksheet read/write APIs. For MaybeAI product-created workbooks or worksheets, use `metadata_output=sidecar` and write metadata to play-be after the workbook/worksheet write succeeds.

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

This skill is primarily a write-time capture skill. Hermes/OpenClaw should capture provenance while creating the workbook/worksheet, then persist the sidecar after the sheet write returns `doc_id` and `gid`. Do not ask the frontend to infer provenance from later edits.

Shared contract: read `context-contract.md` first. It defines the required inputs, sidecar provenance schema, and non-fabrication rules.

## Trigger

Trigger when the user asks any of these:

- track where spreadsheet values came from
- attach source links or citations to cells
- emit `metadata_output=sidecar` records for sheet source overlay or Cell Info
- show whether a value came from `web`, `api`, `file`, `search`, `tool`, `llm`, or `user`
- attach paragraph locators, field paths, snippets, or retrieval notes to cells
- reduce hallucination risk by preserving provenance

Do not use this skill for:

- formula lineage or precedent tracing
- confidence heatmaps
- freshness grading
- sanity, outlier, or unit validation

Use `assess-sheet-confidence` for confidence, freshness, and sanity scoring.

## What To Read

- Always read `context-contract.md`.
- Read `workflow.md` before writing worksheets.
- Read `output-format.md` before producing the final answer.
- Read `verification.md` when you need live verification criteria.
- Read `source-taxonomy.md` when source classification is ambiguous.

## Execution Rules

1. Treat `spreadsheet_url` as required.
2. Prefer `selected_range` as the audit scope. If absent, audit the active worksheet's used range only when the user clearly asked for whole-sheet coverage.
3. Ignore blank cells, `N/A`, `NA`, `null`, `--`, or similar placeholders unless the cell itself is a real error output that should be tracked.
4. Reconstruct provenance from the actual assistant workflow whenever possible:
   - creation run id or session id
   - recent tool-call records
   - tool outputs
   - session history
   - attached citations
   - uploaded or retrieved files
   - opened webpages or search results
5. Classify the source by the strongest real evidence in that workflow:
   - `api`
   - `tool`
   - `file`
   - `web`
   - `search`
   - `llm`
   - `mixed`
   - `user`
6. Never invent a `source_link`, `#fragment`, section title, API field path, tool name, file path, snippet, or date.
7. If evidence is incomplete or model-derived, keep the value but mark it `llm`.
8. Use `metadata_output=sidecar` when the caller is creating a MaybeAI workbook or worksheet for the product UI. Do not create `source-tracking`, `SourceMeta`, hidden helper worksheets, or visible metadata worksheets.
9. Do not use standalone worksheet mode for MaybeAI product documents. Legacy standalone tables are allowed only when the user explicitly asks for workbook-visible audit tables outside the product sidecar flow.
10. `track-sheet-sources` owns provenance fields only. It does not create `<worksheet_name>-source-confident` and does not score confidence colors.
11. Record `source_date_type` and `source_date` when the source exposes them, but do not grade freshness here.
12. If one cell has multiple real sources worth preserving, either:
   - emit multiple rows for the same cell, or
   - classify it as `mixed` and explain the composition in `note`.
13. In sidecar mode, after the worksheet/workbook write succeeds, call play-be cell metadata batch-upsert and provenance-feature/upsert. If either upsert fails, report partial completion and do not claim overlay metadata is available.
14. If `assess-sheet-confidence` is also running in the same creation flow, merge provenance and confidence fields into the same `cell_metadata[]` objects and perform one batch-upsert when practical. Do not write two conflicting records for the same `doc_id + gid + row + col`.
15. After writing, verify sidecar row counts and feature config.
16. If a legacy `source-tracking` table already exists, do not update it unless the user explicitly requested legacy workbook-visible audit output.

## Output Rules

- The workbook change plus sidecar metadata write is the main output in `metadata_output=sidecar` mode.
- The chat response should be short and operational:
  - audited scope
  - metadata output mode
  - row count written to play-be sidecar
  - count by source type
  - source-date coverage
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
