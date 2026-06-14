# Assess Sheet Confidence Verification

Use this checklist to verify that the skill is doing a real confidence assessment instead of decorative formatting.

## Acceptance criteria

### A. Output target

- In `metadata_output=sidecar`, no `<worksheet_name>-source-confident` worksheet is created and workbook styles are unchanged.
- In standalone fallback mode, `<worksheet_name>-source-confident` exists when requested.

### A1. Sidecar metadata quality

For `metadata_output=sidecar`, verify:

- play-be batch-upsert completed after workbook/worksheet creation succeeded
- `provenance-feature/upsert` completed for `doc_id + gid`
- sidecar row count matches assessed data cells after skip rules
- header row 1 and column A were skipped by default unless explicitly overridden
- every row has `doc_id`, `gid`, `cell`, `row`, `col`, `value_hash`, `confidence_level`, and `confidence_reason`
- every `confidence_level` is an integer from `1` through `5`
- unsupported rows use low confidence and empty or explicitly weak evidence instead of fabricated sources
- no workbook style, helper worksheet, or visible cell was changed for metadata

### B. Mirror integrity

In standalone fallback `<worksheet_name>-source-confident`, verify:

- the duplicated sheet or range has the same visible values as the source worksheet
- the duplicated sheet or range keeps the same row and column structure for the audited scope
- percentages, currencies, dates, and other obvious display formats still look like the source sheet after the copy
- cells are colored by confidence tier, not by source type
- no helper text, legend blocks, or raw hex strings were written into visible worksheet cells

### C. Assessment quality

Verify:

- each assessed cell has a non-empty `confidence_level`
- sidecar `confidence_level` values are numeric `1` through `5`
- freshness fields are present when source dates exist
- validation fields are present when sanity review was requested
- outliers are marked `needs_review` rather than automatically `invalid` unless a hard rule is violated
- unsupported rows fall to `very_low` rather than being overstated

### D. Read-back verification

After writing, read the affected worksheets back and confirm:

- representative rows match expected visible values
- representative cells have the expected confidence tier
- any enriched `source-tracking` columns were written as expected

## Minimal expected mirror behavior

| check | expectation |
| --- | --- |
| worksheet name | `Supply Chain Latest-source-confident` |
| duplicated values | same as the source sheet for the audited scope |
| row/column positions | same as source sheet for the audited scope |
| very_high label | `很高` with green fill |
| high label | `高` with light green fill |
| medium label | `中` with yellow fill |
| low label | `低` with orange fill |
| very_low label | `很低` with red fill |
