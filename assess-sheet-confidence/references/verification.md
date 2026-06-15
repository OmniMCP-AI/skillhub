# Assess Sheet Confidence Verification

Use this checklist to verify that the skill is doing a real confidence assessment instead of decorative formatting.

## Acceptance criteria

### A. Output target

- In `metadata_output=sidecar`, no `<worksheet_name>-source-confident` worksheet is created and workbook styles are unchanged.
- No `source-tracking`, `SourceMeta`, `底稿-SourceMeta`, helper worksheet, or visible metadata worksheet is created in product mode.

### A1. Sidecar metadata quality

For `metadata_output=sidecar`, verify:

- authenticated request is used: `Authorization: Bearer <MAYBEAI_API_TOKEN>` or trusted internal headers
- play-be batch-upsert completed after workbook/worksheet creation succeeded
- `provenance-feature/upsert` completed for `doc_id + gid`
- `provenance-feature/detail` returns `source_confidence_enabled=true` for the same owner user, `doc_id`, and `gid`
- sidecar row count matches assessed data cells after skip rules
- header row 1 and column A were skipped by default unless explicitly overridden
- every row has `doc_id`, `gid`, `cell`, `row`, `col`, `value_hash`, `confidence_level`, and `confidence_reason`
- every `confidence_level` is an integer from `1` through `5`
- unsupported rows use low confidence and empty or explicitly weak evidence instead of fabricated sources
- no workbook style, helper worksheet, or visible cell was changed for metadata
- frontend can query `sheet_provenance_feature_config` before rendering and then query `sheet_cell_metadata` only for enabled worksheets
- confidence distribution is plausible for the workbook type; do not accept a uniform whole-workbook score without an explicit reason
- for synthetic/demo workbooks, disclosure, calculation, assumptions, and unsupported real-world claims are scored separately

### A1a. Authentication checks

For product sidecar mode, verify that:

- missing authentication fails instead of silently writing metadata
- `MAYBEAI_API_TOKEN` works for the sheet owner or an editor
- trusted internal mode requires both `X-Internal-Token` and `X-User-Id`
- metadata is stored under the owner user id that the frontend will later query

### A2. Feature toggle contract

For product sidecar mode, verify that:

- enabling confidence tracking uses `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
- the upsert target is the same `doc_id + gid` returned by worksheet creation
- the upsert uses the same owner user id as the metadata rows
- `capture_mode` is `write_time`
- `ignore_header_rows` and `ignore_first_columns` match the cells omitted from metadata
- if source metadata is not written, `source_tracking_enabled` remains false unless a previous verified config should be preserved

### B. Assessment quality

Verify:

- each assessed cell has a non-empty `confidence_level`
- sidecar `confidence_level` values are numeric `1` through `5`
- freshness fields are present when source dates exist
- validation fields are present when sanity review was requested
- outliers are marked `needs_review` rather than automatically `invalid` unless a hard rule is violated
- unsupported rows fall to `very_low` rather than being overstated
- tool-generated cells are not all assigned the same confidence merely because the workbook was written by one script

### B1. Synthetic/demo anti-regression

For simulated reports, mock data, demo workbooks, or script-generated Excel files, sample cells across sheet types and verify:

- explicit demo/synthetic disclaimers are usually `confidence_level=4`, `validation_status=ok`
- formulas, ratios, and reconciled totals are usually `confidence_level=3` when reproducible
- synthetic assumptions and management interpretations are usually `confidence_level=2`
- unsupported real-company factual claims are `confidence_level=1`
- real externally sourced values can be `4` or `5`
- one single level, especially all `2`, is rejected unless the workbook genuinely contains only one claim type

### C. Sidecar read-back verification

After writing, read the affected worksheets back and confirm:

- representative rows match expected visible values
- representative cells have the expected confidence tier
- feature config is enabled for the same `doc_id + gid`
