# Track Sheet Sources Verification

Use this checklist to verify that the skill is doing real provenance capture.

## Acceptance criteria

### A. Output target

- In `metadata_output=sidecar`, no `source-tracking` worksheet is created and workbook styles are unchanged.
- In standalone fallback mode, `source-tracking` exists.

### A1. Sidecar metadata quality

For `metadata_output=sidecar`, verify:

- authenticated request is used: `Authorization: Bearer <MAYBEAI_API_TOKEN>` or trusted internal headers
- play-be batch-upsert completed after workbook/worksheet creation succeeded
- `provenance-feature/upsert` completed for `doc_id + gid`
- `provenance-feature/detail` returns `source_tracking_enabled=true` for the same owner user, `doc_id`, and `gid`
- sidecar row count matches audited data cells after skip rules
- header row 1 and column A were skipped by default unless explicitly overridden
- every row has `doc_id`, `gid`, `cell`, `row`, `col`, `source_type`, `source_refs`, and `value_hash`
- `cell` matches `row` and `col`
- no workbook style, helper worksheet, or visible cell was changed for metadata
- frontend can query `sheet_provenance_feature_config` before rendering and then query `sheet_cell_metadata` only for enabled worksheets
- source distribution is plausible; do not accept an entire generated workbook as `source_type=tool` unless the tool is genuinely the only recoverable provenance surface
- if a tool wrote the workbook, sampled rows preserve `tool_role` in `source_refs[]` and row-level `source_type` reflects the upstream source

### A1a. Authentication checks

For product sidecar mode, verify that:

- missing authentication fails instead of silently writing metadata
- `MAYBEAI_API_TOKEN` works for the sheet owner or an editor
- trusted internal mode requires both `X-Internal-Token` and `X-User-Id`
- metadata is stored under the owner user id that the frontend will later query

### A2. Feature toggle contract

For product sidecar mode, verify that:

- enabling source tracking uses `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
- the upsert target is the same `doc_id + gid` returned by worksheet creation
- the upsert uses the same owner user id as the metadata rows
- `capture_mode` is `write_time`
- `ignore_header_rows` and `ignore_first_columns` match the cells omitted from metadata
- if confidence metadata is not written, `source_confidence_enabled` remains false unless a previous verified config should be preserved

### B. Tracking table quality

For standalone fallback mode, verify:

- the header row matches the contract
- each audited cell has at least one row
- blank and placeholder cells were skipped unless they were true error outputs
- `source_type` is never blank
- `source_link` is blank rather than fabricated when missing
- `source_section` carries paragraph, heading, or field locator when available
- `source_date_type` and `source_date` are present when the source exposes them

### C. Hallucination control

Verify:

- search-only evidence stayed `search` unless the page was actually opened
- unsupported rows stayed `llm`
- synthetic/demo rows use `llm` with `upstream_source_type=synthetic` rather than pretending the workbook writer is the business source
- no fake URL fragments were created
- no fake source dates were written

### C1. Tool-source anti-regression

For script-generated or tool-generated workbooks, sample at least 10 cells across different sheets and verify:

- workbook writer tools such as `openpyxl`, Excelize, or MaybeAI Sheet are recorded as `source_refs[].tool_role=workbook_writer`, not as the row-level primary source for every cell
- calculated fields record calculator evidence separately from the input source
- search, web, file, api, database, llm, and user sources are not collapsed into `tool`
- source type distribution is explained in the final response when one source type exceeds 80%

### D. Read-back verification

After writing, read `source-tracking` back and confirm:

- header cells are present
- row counts match the intended write
- representative audit rows match expected values

## Minimal expected `source-tracking` sample

| worksheet_name | cell | value | source_type | source_link | source_section | source_date_type | source_date | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Sheet1` | `B2` | `123` | `api` | `https://api.example.com/orders/1` | `$.data.order_id` | `effective_date` | `2026-06-10` | `order_id = 123` | `api call` | `` |
| `Sheet1` | `C2` | `ACME` | `web` | `https://example.com/product/acme` | `Specs > Brand` | `publish_date` | `2025-11-03` | `Brand: ACME` | `opened page` | `normalized casing` |
| `Sheet1` | `D2` | `2025 estimate` | `llm` | `` | `` | `` | `` | `` | `llm synthesis` | `no direct source found` |
