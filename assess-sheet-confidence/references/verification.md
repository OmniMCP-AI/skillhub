# Assess Sheet Confidence Verification

Use this checklist to verify that the skill is doing a real confidence assessment instead of decorative formatting.

## Acceptance criteria

### A. Worksheet existence

- `<worksheet_name>-source-confident` exists when requested

### B. Mirror integrity

In `<worksheet_name>-source-confident`, verify:

- the duplicated sheet or range has the same visible values as the source worksheet
- the duplicated sheet or range keeps the same row and column structure for the audited scope
- percentages, currencies, dates, and other obvious display formats still look like the source sheet after the copy
- cells are colored by confidence tier, not by source type
- no helper text, legend blocks, or raw hex strings were written into visible worksheet cells

### C. Assessment quality

Verify:

- each assessed cell has a non-empty `confidence_level`
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
