---
name: source-tracking-confident
description: Audits spreadsheet values for provenance, freshness, sanity, and hallucination risk. Use when the user wants to mark each cell by source type such as web/api/search/llm, assign confidence levels, expose source dates or effective dates, flag unit or magnitude issues or outliers for review, color-code a worksheet with a five-level confidence legend, and create source tracking worksheets with links and evidence snippets.
---

# Source Tracking Confident

Use this skill when the goal is provenance auditing and confidence visualization for spreadsheet values. This is an execution-layer skill for OpenClaw, Hermes, or any AI assistant that has access to conversation context, session history, tool-call traces, and spreadsheet write tools. It does not require new backend code.

Primary dependency: use the `maybeai-sheet` skill and its existing worksheet read/write/style APIs.

Shared contract: read `context-contract.md` first. It defines the required inputs, source taxonomy, output worksheets, and the non-fabrication rules for links and anchors.

## Trigger

Trigger when the user asks any of these:

- mark spreadsheet values by source type
- show confidence level for generated cells
- show source publish date, modified date, effective date, or freshness
- validate whether values look unreasonable, use wrong units, are too large or too small, or are outliers
- reduce or expose LLM hallucination risk
- create source audit / provenance / tracking worksheets
- attach links, citations, paragraphs, snippets, or evidence rows to spreadsheet cells
- color cells by confidence with a five-level legend

Strong hints include terms like `source tracking`, `confidence`, `citation`, `hallucination`, `来源`, `可信度`, `证据`, `tracking worksheet`, `source-confident`, `source-tracking`.

Do not use this skill for formula lineage. Use `analyze-sheet-lineage` for cell dependency tracing.

## What To Read

- Always read `context-contract.md`.
- Read `workflow.md` before writing or styling worksheets.
- Read `output-format.md` before producing the final answer.
- Read `verification.md` when you need a live verification checklist or acceptance criteria.
- Read `source-taxonomy.md` when source type or confidence tier is ambiguous.

## Execution Rules

1. Treat `spreadsheet_url` as required.
2. Prefer `selected_range` as the audit scope. If absent, audit the active worksheet's used range only when the user clearly asked for whole-sheet coverage.
3. Ignore blank cells, `N/A`, `NA`, `null`, `--`, or similar placeholder cells unless the cell itself is clearly an error value that should be tracked.
4. Reconstruct provenance from the actual assistant workflow whenever possible:
   - recent tool-call records
   - tool outputs
   - session history
   - citations already attached to the answer
   - uploaded files or retrieved files
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
6. Never invent a `source_link`, `#fragment`, section title, API field path, tool name, file path, or evidence snippet.
7. If evidence is incomplete or model-derived, keep the value but mark it `llm` and `very_low`.
8. Create or refresh two worksheet outputs:
   - worksheet-local confidence mirror: `<worksheet_name>-source-confident`
   - consolidated audit table: `source-tracking`
9. Use a five-level confidence legend unless the user asks otherwise:
   - very_high: `#b6d7a8`
   - high: `#d9ead3`
   - medium: `#fff2cc`
   - low: `#f9cb9c`
   - very_low: `#f4cccc`
10. Track source freshness separately from confidence:
   - prefer `effective_date`
   - otherwise use `publish_date`
   - otherwise use `modified_date`
   - if none exist, leave the date blank and mark freshness uncertainty in `note`
11. High confidence does not imply fresh data. A row may be `very_high` or `high` confidence and still be stale.
12. Run a lightweight sanity validation pass when the request or domain benefits from it:
   - unit consistency
   - obvious magnitude errors
   - impossible ranges
   - outlier review
13. Do not treat outliers as automatic errors. Mark them `needs_review` unless there is a stronger rule proving they are invalid.
14. Use `maybeai-sheet` write/style APIs only. Do not assume a special provenance API exists.
15. After writing, read both worksheets back and verify the expected rows and styles were written.
16. If both tool history and final answer text exist, trust tool history first. Do not downgrade a verifiable API/tool/file source to `llm` just because the final answer is paraphrased.
17. If the final answer mixes multiple upstream sources, either:
   - emit multiple tracking rows for the same cell, or
   - classify it as `mixed` and explain the composition in `note`.
18. The `<worksheet_name>-source-confident` sheet should duplicate the original worksheet content for the audited scope:
   - same row numbers
   - same column positions
   - same visible cell values
   - no extra audit columns inserted into the copied grid
19. Apply confidence colors onto that duplicated grid only after the values are copied.
20. Put legends or audit metadata only outside the copied data region, so the mirrored content stays structurally identical to the source sheet/range.
21. Respect worksheet naming limits. If `<worksheet_name>-source-confident` exceeds the workbook engine's sheet-name limit, shorten it deterministically while preserving readability, for example:
   - preferred: `<worksheet_name>-source-confident`
   - fallback: `<worksheet_name>-src-conf`
   - if still too long, truncate the worksheet-name prefix and keep the suffix stable

## Output Rules

- The workbook change is the main output.
- The chat response should be short and operational:
  - audited scope
  - created or updated worksheets
  - confidence legend
  - freshness summary
  - sanity summary
  - row counts by source type / confidence tier
  - verification result
- If live modification was not executed, say so clearly and provide the exact next step.
