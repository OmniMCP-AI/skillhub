# Assess Sheet Confidence Output Format

Use this structure for the final answer after the workbook write is complete.

## 1. Summary

- `scope`: audited worksheet/range
- `created_or_updated`: `<worksheet_name>-source-confident` and any enriched worksheets
- `confidence_legend`: readable labels only, for example `很高 / 高 / 中 / 低 / 很低`
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

## 3. Workbook changes

Example:

- `Supply Chain Latest-source-confident`: duplicated the source worksheet content and colored the duplicated cells by confidence
- `source-tracking`: refreshed confidence, freshness, and validation columns for the audited rows

## 4. Risks or unresolved cells

Only include this when needed.

Example:

- one row stayed `very_low` because no stable source evidence was available
- one row was marked `stale` because the source date was too old for the question
- two rows were marked `needs_review` because the magnitude looked unusual, but not provably wrong

## Anti-patterns

Do not output:

- raw hex color strings like `#d9ead3` in user-facing worksheet cells or legend text
- a generic claim that everything is high confidence
- a generic claim that everything is fresh
- a generic claim that every outlier is an error
- long prose instead of the actual workbook write result
