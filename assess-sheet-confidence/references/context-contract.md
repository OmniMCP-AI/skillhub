# Assess Sheet Confidence Context Contract

## Required input

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`

## Preferred inputs

- `[selected_range=Sheet1!B2:D20]`
- `[metadata_output=sidecar]` for MaybeAI product workbook/worksheet creation
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

## Output modes

Preferred product mode:

1. `metadata_output=sidecar`

Fallback standalone mode:

1. worksheet-local confidence mirror: `<worksheet_name>-source-confident`
2. optionally enriches `source-tracking`

In `metadata_output=sidecar` mode:

- do not create `<worksheet_name>-source-confident`
- do not create `source-tracking`
- do not modify workbook styles or visible cell values
- emit normalized `cell_metadata[]`
- after the workbook or worksheet write succeeds, call play-be cell metadata batch-upsert
- call `provenance-feature/upsert` so the frontend can discover source confidence for `doc_id + gid`

When calling play-be from Hermes/OpenClaw or another trusted creation flow, use the internal write identity:

| header | value |
| --- | --- |
| `X-Internal-Token` | `SETTINGS.run_task_token` or the configured service token |
| `X-User-Id` | owner user id that should own the sheet metadata |
| `X-User-Email` | optional owner email |

Use standalone mirror mode only when the metadata backend is unavailable, the caller has no play-be write context, or the user explicitly asks for workbook-visible confidence coloring.

`<worksheet_name>` means the worksheet resolved from `gid` or an explicit worksheet target.

If the preferred mirror name exceeds the worksheet-name limit, shorten it deterministically:

- first fallback: `<worksheet_name>-src-conf`
- second fallback: truncate the worksheet-name prefix and keep `-src-conf`

## Confidence levels

Sidecar mode stores numeric levels:

| level | label | meaning |
| --- | --- | --- |
| `1` | `很低` | unsupported, model-derived, or trace too weak |
| `2` | `低` | weak evidence, estimated mapping, or strong ambiguity |
| `3` | `中` | evidence exists but is partial, inferred, or indirect |
| `4` | `高` | good direct evidence with minor transformation or recency risk |
| `5` | `很高` | direct reproducible evidence with tight value match |

`confidence_score` is optional and must stay between `0` and `1`.

Standalone mirror mode may still use text tiers:

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

## Sidecar `cell_metadata[]` contract

Each assessed data cell in sidecar mode emits one normalized object compatible with play-be batch-upsert.

Required identity and coordinate fields:

| field | meaning |
| --- | --- |
| `doc_id` | MaybeAI spreadsheet document id parsed from `spreadsheet_url` or creation result |
| `gid` | worksheet gid from the target worksheet or creation result |
| `worksheet_name` | worksheet name when known |
| `cell` | A1 cell such as `B2` |
| `row` | 1-based row number |
| `col` | 1-based column number |

Required assessment fields:

| field | meaning |
| --- | --- |
| `confidence_level` | integer `1` to `5` |
| `confidence_score` | optional numeric score between `0` and `1` |
| `confidence_reason` | short reason a reviewer can understand |
| `value_hash` | stable hash of the visible value at write time, used for stale detection |

Recommended provenance and validation fields:

| field | meaning |
| --- | --- |
| `value_preview` | short visible value preview, truncated when needed |
| `source_type` | `database/api/tool/file/document/web/search/multimedia/llm/mixed/user` when known |
| `source_refs` | array of real source references; use `[]` when no stable evidence exists |
| `freshness_level` | `current/aging/stale/unknown` |
| `freshness_note` | explanation of the freshness decision |
| `validation_status` | `ok/needs_review/invalid/unknown` |
| `validation_type` | `unit/range/magnitude/outlier/cross_field_consistency/manual_review` |
| `validation_note` | explanation of the sanity assessment |

Default product skip rules exclude header row 1 and column A unless explicitly overridden.

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
