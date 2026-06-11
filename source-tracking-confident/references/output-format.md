# Source Tracking Output Format

Use this structure for the final answer after the workbook write is complete.

## 1. Summary

- `scope`: audited worksheet/range
- `created_or_updated`: `<worksheet_name>-source-confident`, `source-tracking`
- `confidence_legend`: very_high / high / medium / low / very_low
- `freshness_summary`: current / aging / stale / unknown
- `sanity_summary`: ok / needs_review / invalid / unknown
- `verification`: passed / partial / failed

## 2. Short stats

Use a compact Markdown table when useful:

| metric | value |
| --- | --- |
| audited_cells | 12 |
| very_high_confidence | 5 |
| high_confidence | 2 |
| medium_confidence | 3 |
| low_confidence | 1 |
| very_low_confidence | 1 |
| current_sources | 4 |
| aging_sources | 5 |
| stale_sources | 1 |
| unknown_freshness | 2 |
| validation_ok | 8 |
| validation_needs_review | 3 |
| validation_invalid | 1 |
| web_sources | 5 |
| api_sources | 4 |
| search_sources | 1 |
| llm_sources | 2 |

## 3. Workbook changes

State where the data was written.

Example:

- `Supply Chain Latest-source-confident`: duplicated the source worksheet content for the audited scope and colored the duplicated cells by confidence
- `source-tracking`: wrote 12 audit rows with source links, paragraph locators, and source dates
- `source-tracking`: also wrote sanity-validation fields for unit, range, magnitude, or outlier review

## 4. Risks or unresolved cells

Only include this when needed.

Example:

- `Sheet1!D8` stayed `llm/very_low` because no real source link was available
- two `search` rows were not upgraded to canonical `web` evidence
- one `web/high` row was still marked `stale` because the publish date was too old for the question
- two rows were marked `needs_review` because the magnitude looked unusual, but not provably wrong

## Recommended worksheet examples

### `<worksheet_name>-source-confident` mirror view

Use an exact mirror plus colored values:

| cell | meaning |
| --- | --- |
| mirrored grid | same row/column positions and same visible values as the source worksheet/range |
| right-side area outside used range | optional legend rows for very_high / high / medium / low / very_low |
| right-side area outside used range | optional scope / worksheet metadata |

### `source-tracking` header

Use this exact header row:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date_type | source_date | freshness_level | freshness_note | validation_status | validation_type | validation_note | source_link | source_section | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Anti-patterns

Do not output:

- a generic claim that everything is high confidence
- a generic claim that everything is fresh
- a generic claim that every outlier is an error
- fake anchors like `#xyz` when the page has no real fragment
- fake publish dates or modified dates
- huge raw JSON blobs in worksheet cells
- long prose instead of the actual workbook write result
