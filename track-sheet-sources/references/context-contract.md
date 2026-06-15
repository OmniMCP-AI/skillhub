# Track Sheet Sources Context Contract

## Required input

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`

## Preferred inputs

- `[selected_range=Sheet1!B2:D20]`
- `[metadata_output=sidecar]` for MaybeAI product workbook/worksheet creation
- `[maybeai_api_token=$MAYBEAI_API_TOKEN]` for authenticated play-be API calls
- `[created_by_run_id=<hermes_or_openclaw_run_id>]`
- `[owner_user_id=<user_id>]` when using internal play-be metadata writes
- `[owner_user_email=<email>]` when available
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

## Output mode

Product mode:

1. `metadata_output=sidecar`

In `metadata_output=sidecar` mode:

- do not create `source-tracking`
- do not create `SourceMeta`, `底稿-SourceMeta`, or visible metadata worksheets
- do not create helper worksheets
- do not modify workbook styles or visible cell values
- emit normalized `cell_metadata[]`
- after the workbook or worksheet write succeeds, call play-be cell metadata batch-upsert
- call `provenance-feature/upsert` so the frontend can discover source tracking for `doc_id + gid`
- store metadata for the owner user id, not for the service account, so normal frontend queries can read it
- treat `doc_id + gid + row + col` as the durable upsert identity

Default play-be base URL:

```text
http://play-be.omnimcp.ai/
```

Use a caller-provided local or staging base URL only when the execution environment explicitly overrides it.

## Authentication

These play-be metadata APIs require authentication.

Default authenticated mode, matching `maybeai-sheet`:

```bash
export MAYBEAI_API_TOKEN=your_token_here
```

Send this header on every play-be metadata request:

```text
Authorization: Bearer <MAYBEAI_API_TOKEN>
```

Trusted internal creation mode:

| header | value |
| --- | --- |
| `X-Internal-Token` | `SETTINGS.run_task_token` or the configured service token |
| `X-User-Id` | owner user id that should own the sheet metadata |
| `X-User-Email` | optional owner email |

Use one authentication mode per request. Do not send metadata as a generic service user unless the owner user id is also supplied through trusted internal headers.

Do not use standalone worksheet mode for MaybeAI product documents. If the user explicitly asks for a workbook-visible audit table, treat it as a legacy/export-only request and make clear that it is not the product overlay source.

It does not own `<worksheet_name>-source-confident`.

## Product write-time capture flow

Use this flow when Hermes/OpenClaw creates a MaybeAI workbook or worksheet:

1. Build a creation-context map while collecting data, before writing the sheet.
2. For each future data cell, keep `source_type`, `source_refs`, evidence excerpt, source date, retrieval method, and the original visible value.
3. Write the workbook/worksheet through the normal MaybeAI Sheet path.
4. Read the write result and resolve `doc_id`, `gid`, and worksheet name.
5. Convert the creation-context map to `cell_metadata[]` with A1 coordinates and `value_hash`.
6. Batch-upsert to play-be.
7. Upsert feature config with `source_tracking_enabled=true`.
8. Query back representative cells or the target range before claiming the overlay is available.

Do not derive provenance from frontend edits, pasted values, or later user updates in the current product plan. If the visible value changes after creation, the frontend may show stale metadata by comparing `value_hash`, but this skill should not repair that metadata unless a new AI-assisted creation/rewrite flow is run.

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
| `created_by_run_id` | Hermes/OpenClaw run/session id when available |
| `metadata_version` | sidecar schema version, currently `1` |

`source_refs[]` should use only real evidence fields. Recommended keys include `source_id`, `source_type`, `title`, `url`, `file_id`, `file_name`, `api_endpoint`, `tool_name`, `tool_role`, `upstream_source_type`, `field_path`, `section`, `page`, `timestamp`, `retrieved_at`, `excerpt`, and `evidence_excerpt`. Do not fabricate URLs, fragments, file ids, field paths, source dates, or excerpts.

Tool/source rule:

- row-level `source_type` should describe the upstream business/data source, not merely the tool that wrote the cell
- use `source_refs[].source_type="tool"` only to preserve the execution method
- use `source_refs[].tool_role` for writer/calculator/extractor/searcher/api_client/database_client
- use `source_refs[].upstream_source_type` when the tool's input source is known, for example `synthetic`, `llm`, `web`, `api`, `file`, or `database`

When confidence has already been assessed by the caller, the same sidecar object may include `confidence_level`, `confidence_score`, and `confidence_reason`; otherwise omit them.

## Play-be request shape

Batch metadata write:

```json
{
  "doc_id": "6a2e9066d2e8a62c0082e081",
  "gid": "0",
  "items": [
    {
      "worksheet_name": "ConfidenceE2E",
      "cell": "B2",
      "row": 2,
      "col": 2,
      "value_preview": "FP&A Lead Agent",
      "value_hash": "sha256:<hash>",
      "source_type": "llm",
      "source_refs": [
        {
          "source_type": "tool",
          "tool_name": "openpyxl",
          "tool_role": "workbook_writer",
          "upstream_source_type": "synthetic",
          "section": "build_report.py synthetic financial model",
          "evidence_excerpt": "FP&A Lead Agent generated as demo workbook content"
        }
      ],
      "evidence_excerpt": "FP&A Lead Agent",
      "metadata_version": 1,
      "created_by_run_id": "run_123"
    }
  ]
}
```

Feature config write:

```json
{
  "doc_id": "6a2e9066d2e8a62c0082e081",
  "gid": "0",
  "source_tracking_enabled": true,
  "source_confidence_enabled": false,
  "capture_mode": "write_time",
  "ignore_header_rows": 1,
  "ignore_first_columns": 1,
  "metadata_version": 1
}
```

## Legacy worksheet layout

The following layout is legacy-only and must not be created during MaybeAI product workbook generation unless the user explicitly asks for a workbook-visible audit table.

### `source-tracking`

Do not create this worksheet for MaybeAI product documents.

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
