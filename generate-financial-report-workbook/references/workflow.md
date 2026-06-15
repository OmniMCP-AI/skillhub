# Financial Report Workbook Workflow

## Step 1: Understand The User Goal

Accept simple user prompts such as:

- `生成财务分析报告 Excel`
- `参考珀莱雅、韩束颗粒度生成快消护肤企业财务报告`
- `做一个老板审阅版财务分析 workbook`

Do not ask the user to specify source tracking or confidence metadata. This workflow handles it automatically.

## Step 2: Decide Data Mode

Classify the task:

| mode | when | workbook labeling |
| --- | --- | --- |
| `real_data` | user provides files/API/database, or structured public data is fetched | cite source and effective date |
| `public_benchmark_plus_synthetic` | public data calibrates ranges but final company is simulated | label values as demo/synthetic and cite benchmark sources |
| `synthetic_demo` | no real data and user asks for simulation/demo | visibly label as demo/synthetic |

If the workbook contains any synthetic/demo data, add visible labels in the cover/assumptions/limitations section. Do not imply the values are real company facts.

## Step 3: Gather Evidence

Use available capabilities:

- Akshare for public finance data when installed.
- Tavily/Serper for public company reports, industry context, and annual-report references.
- User files or existing workbooks when provided.
- Opened web/PDF/document pages when available.

Record a source manifest while gathering evidence. Keep enough detail to build cell metadata after the workbook is written:

- source type
- URL/file/API endpoint/tool name
- field path or section
- source date or retrieved_at
- evidence excerpt
- whether the cell is real data, benchmark, synthetic assumption, formula/calculation, or disclosure text

## Step 4: Generate Workbook

Generate the workbook with user-facing business sheets only. For finance management reports, a common structure is:

1. `封面`
2. `老板摘要`
3. `经营概览`
4. `利润分析`
5. `资产负债分析`
6. `现金流分析`
7. `关键指标`
8. `风险与建议`
9. `追问支持`
10. optional `限制与审核`

Avoid merged title rows that break MaybeAI readback headers. Prefer row 1 as clean column headers.

Keep the workbook business-facing. Store source/confidence details in play-be sidecar metadata so the product UI can render overlays and Cell Info without adding metadata sheets.

## Step 5: Upload Or Create MaybeAI Sheet

Use MaybeAI Sheet/play-be APIs with:

```text
Authorization: Bearer <MAYBEAI_API_TOKEN>
```

Capture:

- `doc_id`
- worksheet `gid`
- worksheet names
- final visible cell values

## Step 6: Build Sidecar Metadata

For each non-header data cell, build one `cell_metadata[]` item.

Default skip rule:

- skip row 1 as header
- skip column A only when it is an ID/label column, not when it contains real data requiring provenance

Use sidecar fields compatible with play-be:

- `doc_id`, `gid`, `worksheet_name`
- `cell`, `row`, `col`
- `value_preview`, `value_hash`
- `source_type`, `source_refs`
- `confidence_level`, `confidence_score`, `confidence_reason`
- `freshness_level`, `validation_status`, `validation_type`, `validation_note`
- `metadata_version=1`, `created_by_run_id` when available

## Step 7: Write Sidecar Metadata

For every worksheet that has metadata:

1. call `POST http://play-be.omnimcp.ai/api/v1/sheet/cell-metadata/batch-upsert`
2. call `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
3. set both backend flags as appropriate, even if the UI exposes one combined Source/Confidence control:
   - `source_tracking_enabled=true`
   - `source_confidence_enabled=true`
   - `capture_mode=write_time`
   - `ignore_header_rows=1`
   - `ignore_first_columns` matching actual skip rules

If updating only one flag, preserve the other flag by querying `provenance-feature/detail` first.

Cell metadata identity is `doc_id + gid + row + col`. Do not create user-specific duplicate metadata rows for the same cell. `user_id` is retained only as audit/last-writer information after document permission checks pass.

## Step 8: Verify

Before final response:

- query representative metadata rows through `cell-metadata/query`
- verify feature config through `provenance-feature/detail`
- verify source distribution is not incorrectly all `tool`
- verify confidence distribution is not incorrectly all `2`
- verify no visible source/confidence worksheet was created or updated in the product workbook
- if visible metadata worksheets exist in the product workbook from a previous run, do not treat them as success evidence; write sidecar metadata and report the legacy worksheets as cleanup debt
