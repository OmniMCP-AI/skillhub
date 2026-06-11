# Assess Sheet Confidence Context Contract

## Required input

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`

## Preferred inputs

- `[selected_range=Sheet1!B2:D20]`
- existing `source-tracking` worksheet
- session history or tool-call records if confidence depends on how the value was produced
- existing source dates, links, snippets, or notes

If `selected_range` is missing, assess the narrowest safe scope. Do not silently expand to the whole workbook unless the user explicitly asked for it.

## Skip rules

Skip cells that are:

- blank
- `N/A`
- `NA`
- `null`
- `--`
- other obvious placeholders with no analytical value

Exception:

- if the cell is a real spreadsheet error or broken generated output, keep it in scope and mark that in `note`

## Output worksheets

This skill creates or refreshes:

1. worksheet-local confidence mirror: `<worksheet_name>-source-confident`
2. optionally enriches `source-tracking`

`<worksheet_name>` means the worksheet resolved from `gid` or an explicit worksheet target.

If the preferred mirror name exceeds the worksheet-name limit, shorten it deterministically:

- first fallback: `<worksheet_name>-src-conf`
- second fallback: truncate the worksheet-name prefix and keep `-src-conf`

## Confidence tiers

- `very_high`
  - score `>= 0.9`
  - internal style color `#b6d7a8`
- `high`
  - score `>= 0.75` and `< 0.9`
  - internal style color `#d9ead3`
- `medium`
  - score `>= 0.5` and `< 0.75`
  - internal style color `#fff2cc`
- `low`
  - score `>= 0.25` and `< 0.5`
  - internal style color `#f9cb9c`
- `very_low`
  - score `< 0.25`
  - internal style color `#f4cccc`

These colors are implementation details for styling only. Do not write the hex strings into user-visible worksheet cells.

Readable labels:

- `很高`
- `高`
- `中`
- `低`
- `很低`

## Freshness fields

Preferred date priority:

1. `effective_date`
2. `publish_date`
3. `modified_date`
4. `retrieved_at`

Freshness labels:

- `current`
- `aging`
- `stale`
- `unknown`

## Validation fields

Allowed `validation_status` values:

- `ok`
- `needs_review`
- `invalid`
- `unknown`

Recommended `validation_type` values:

- `unit`
- `range`
- `magnitude`
- `outlier`
- `cross_field_consistency`
- `manual_review`

## Assessment schema

When this skill enriches `source-tracking`, it should use these fields:

| field | meaning |
| --- | --- |
| `confidence_level` | `very_high/high/medium/low/very_low` |
| `confidence_score` | numeric score between `0` and `1` |
| `freshness_level` | `current/aging/stale/unknown` |
| `freshness_note` | explanation of the freshness decision |
| `validation_status` | `ok/needs_review/invalid/unknown` |
| `validation_type` | `unit/range/magnitude/outlier/cross_field_consistency/manual_review` |
| `validation_note` | explanation of the sanity assessment |

## Worksheet layout

### `<worksheet_name>-source-confident`

Required behavior:

- duplicate the original worksheet content for the audited scope
- keep the same row numbers, column positions, and visible values
- do not insert extra audit columns or helper blocks into the mirrored grid
- color duplicated cells by confidence tier
- preserve visible formatting such as percentages, currencies, and dates

### `source-tracking`

If present, keep the provenance columns and add assessment columns. Preferred combined header shape:

| worksheet_name | cell | value | source_type | source_link | source_section | source_date_type | source_date | evidence_excerpt | retrieval_method | confidence_level | confidence_score | freshness_level | freshness_note | validation_status | validation_type | validation_note | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
