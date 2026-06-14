# Track Sheet Sources Context Contract

## Required input

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`

## Preferred inputs

- `[selected_range=Sheet1!B2:D20]`
- `[metadata_output=sidecar]` for MaybeAI product workbook/worksheet creation
- explicit worksheet or cell targets from the user
- recent tool-call records and raw tool outputs
- session history
- answer citations already attached
- uploaded files, retrieved files, opened pages, or search result snippets

If `selected_range` is missing, audit the narrowest safe scope. Do not silently expand to the whole workbook unless the user explicitly asked for it.

## Skip rules

Skip cells that are:

- blank
- `N/A`
- `NA`
- `null`
- `--`
- other obvious placeholders with no analytical value

Exception:

- if the cell is a real spreadsheet error or broken generated output, keep it in scope and note that explicitly

## Assistant-context rule

This skill is assistant-agnostic. It should work for OpenClaw, Hermes, or any AI assistant that can inspect execution context.

When deciding where a spreadsheet value came from, use this evidence order:

1. recent tool-call records and raw tool outputs
2. explicit citations already attached to the answer
3. retrieved files or uploaded files
4. opened canonical webpages or PDFs
5. search snippets
6. final LLM answer text by itself

If the final answer says something but the tool history proves a different upstream source, trust the tool history.

## Output modes

Preferred product mode:

1. `metadata_output=sidecar`

Fallback standalone mode:

1. `source-tracking`

In `metadata_output=sidecar` mode:

- do not create `source-tracking`
- do not create helper worksheets
- do not modify workbook styles or visible cell values
- emit normalized `cell_metadata[]`
- after the workbook or worksheet write succeeds, call play-be cell metadata batch-upsert
- call `provenance-feature/upsert` so the frontend can discover source tracking for `doc_id + gid`

When calling play-be from Hermes/OpenClaw or another trusted creation flow, use the internal write identity:

| header | value |
| --- | --- |
| `X-Internal-Token` | `SETTINGS.run_task_token` or the configured service token |
| `X-User-Id` | owner user id that should own the sheet metadata |
| `X-User-Email` | optional owner email |

Use standalone worksheet mode only when the metadata backend is unavailable, the caller has no play-be write context, or the user explicitly asks for a workbook-visible audit table.

It does not own `<worksheet_name>-source-confident`.

## Source taxonomy

Allowed `source_type` values:

- `database`
- `web`
- `api`
- `tool`
- `file`
- `document`
- `search`
- `multimedia`
- `llm`
- `mixed`
- `user`

Read `source-taxonomy.md` when classification is ambiguous.

## Base provenance schema

Each audited cell should produce at least one normalized record with these fields:

| field | meaning |
| --- | --- |
| `worksheet_name` | original worksheet name |
| `cell` | original A1 cell |
| `value` | visible value being audited |
| `source_type` | `web/api/tool/file/search/llm/mixed/user` |
| `source_link` | canonical URL or doc URL; may include `#fragment` only when real |
| `source_section` | heading, paragraph locator, API field path, tool output locator, file section, or search-result note |
| `source_date_type` | `effective_date/publish_date/modified_date/retrieved_at` when known |
| `source_date` | ISO date or datetime string when known |
| `evidence_excerpt` | short snippet proving the value |
| `retrieval_method` | how the evidence was obtained |
| `note` | ambiguity, fallback, or verification note |

## Sidecar `cell_metadata[]` contract

Each audited data cell in sidecar mode emits one normalized object compatible with play-be batch-upsert.

Required identity and coordinate fields:

| field | meaning |
| --- | --- |
| `doc_id` | MaybeAI spreadsheet document id parsed from `spreadsheet_url` or creation result |
| `gid` | worksheet gid from the target worksheet or creation result |
| `worksheet_name` | worksheet name when known |
| `cell` | A1 cell such as `B2` |
| `row` | 1-based row number |
| `col` | 1-based column number |

Required provenance fields:

| field | meaning |
| --- | --- |
| `source_type` | `database/api/tool/file/document/web/search/multimedia/llm/mixed/user` |
| `source_refs` | array of real source references; use `[]` when no stable evidence exists |
| `value_hash` | stable hash of the visible value at write time, used for stale detection |

Recommended display and audit fields:

| field | meaning |
| --- | --- |
| `value_preview` | short visible value preview, truncated when needed |
| `source_date_type` | `effective_date/publish_date/modified_date/retrieved_at` when known |
| `source_date` | ISO date or datetime string when known |
| `evidence_excerpt` | short non-sensitive excerpt proving the value |
| `retrieval_method` | how the evidence was obtained |
| `note` | ambiguity, fallback, or verification note |

`source_refs[]` should use only real evidence fields. Recommended keys include `type`, `title`, `url`, `file_id`, `file_name`, `api_endpoint`, `tool_name`, `field_path`, `section`, `page`, `timestamp`, `retrieved_at`, and `evidence_excerpt`. Do not fabricate URLs, fragments, file ids, field paths, source dates, or excerpts.

When confidence has already been assessed by the caller, the same sidecar object may include `confidence_level`, `confidence_score`, and `confidence_reason`; otherwise omit them.

## Worksheet layout

### `source-tracking`

Minimum base header:

| worksheet_name | cell | value | source_type | source_link | source_section | source_date_type | source_date | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Compatibility rule:

- if `source-tracking` already contains extra columns from `assess-sheet-confidence`, preserve them when feasible
- do not remove confidence, freshness, or validation columns unless the user explicitly asked to rebuild the sheet from scratch

## Non-fabrication rules

- Only append `#fragment` to `source_link` when the page or document actually exposes that fragment.
- If there is no real fragment, keep the base URL in `source_link` and put the locator in `source_section`.
- If the evidence came only from a search snippet and the underlying page was not opened, classify it as `search`.
- If the value came from model synthesis without direct evidence, classify it as `llm`.
- Do not infer a fake `publish_date`, `modified_date`, or `effective_date`.
