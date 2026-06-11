# Track Sheet Sources Output Format

Use this structure for the final answer after the workbook write is complete.

## 1. Summary

- `scope`: audited worksheet/range
- `created_or_updated`: `source-tracking`
- `source_summary`: counts by source type
- `date_coverage`: how many rows have usable source dates
- `verification`: passed / partial / failed

## 2. Short stats

Use a compact Markdown table when useful:

| metric | value |
| --- | --- |
| audited_cells | 12 |
| tracking_rows_written | 12 |
| web_sources | 5 |
| api_sources | 4 |
| file_sources | 1 |
| search_sources | 1 |
| llm_sources | 1 |
| rows_with_source_date | 8 |
| rows_without_source_date | 4 |

## 3. Workbook changes

Example:

- `source-tracking`: wrote 12 provenance rows with source links, locators, snippets, retrieval method, and source dates

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
