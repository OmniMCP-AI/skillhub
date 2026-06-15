# Track Sheet Sources Output Format

Use this structure for the final answer after the workbook write is complete.

## 1. Summary

- `scope`: audited worksheet/range
- `metadata_output`: `sidecar`
- `created_or_updated`: play-be sidecar metadata and provenance feature config
- `feature_config`: whether `source_tracking_enabled` is on for the target `doc_id + gid`
- `source_summary`: counts by source type
- `date_coverage`: how many rows have usable source dates
- `verification`: passed / partial / failed

## 2. Short stats

Use a compact Markdown table when useful:

| metric | value |
| --- | --- |
| audited_cells | 12 |
| sidecar_rows_written | 12 |
| source_tracking_enabled | true |
| web_sources | 5 |
| api_sources | 4 |
| file_sources | 1 |
| search_sources | 1 |
| llm_sources | 1 |
| rows_with_source_date | 8 |
| rows_without_source_date | 4 |

## 3. Workbook changes

Example:

- `metadata_output=sidecar`: wrote 12 provenance metadata rows to play-be and enabled source tracking for the worksheet through `http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`; no `source-tracking`, `SourceMeta`, `底稿-SourceMeta`, helper worksheet, or style changes were created or updated in the product workbook

## 4. Risks or unresolved cells

Only include this when needed.

Example:

- two rows stayed `search` because the canonical page was never opened
- one row stayed `llm` because no stable source evidence was available
- three rows had no reliable source date

## Anti-patterns

Do not output:

- confidence-tier summaries as if this skill scored confidence
- freshness or validation claims as if this skill assessed them
- fake anchors like `#xyz` when the page has no real fragment
- fake publish dates or modified dates
- long prose instead of the actual workbook write result
