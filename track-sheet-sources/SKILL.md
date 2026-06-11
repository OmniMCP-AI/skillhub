---
name: track-sheet-sources
description: Tracks spreadsheet value provenance and writes source-tracking audit rows with source type, links, section locators, evidence snippets, retrieval method, and source dates. Use when the user wants to know where sheet values came from, attach citations to cells, or create or refresh a source-tracking worksheet. This skill focuses on provenance, not confidence coloring.
---

# Track Sheet Sources

Use this skill when the goal is source provenance for spreadsheet values. It is for OpenClaw, Hermes, or any AI assistant that can inspect execution context such as tool-call traces, session history, attached citations, uploaded files, and opened pages.

Primary dependency: use the `maybeai-sheet` skill and its existing worksheet read/write APIs.

Shared contract: read `context-contract.md` first. It defines the required inputs, the base `source-tracking` schema, and the non-fabrication rules.

## Trigger

Trigger when the user asks any of these:

- track where spreadsheet values came from
- attach source links or citations to cells
- create or refresh a `source-tracking` worksheet
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
8. Create or refresh `source-tracking`.
9. `track-sheet-sources` owns provenance fields only. It does not create `<worksheet_name>-source-confident` and does not score confidence colors.
10. Record `source_date_type` and `source_date` when the source exposes them, but do not grade freshness here.
11. If one cell has multiple real sources worth preserving, either:
   - emit multiple rows for the same cell, or
   - classify it as `mixed` and explain the composition in `note`.
12. Use `maybeai-sheet` write APIs only. Do not assume a special provenance backend exists.
13. After writing, read `source-tracking` back and verify the expected rows were written.
14. If a richer `source-tracking` table already exists, preserve extra non-provenance columns when feasible instead of deleting them blindly.

## Output Rules

- The workbook change is the main output.
- The chat response should be short and operational:
  - audited scope
  - created or updated worksheets
  - row count written to `source-tracking`
  - count by source type
  - source-date coverage
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
