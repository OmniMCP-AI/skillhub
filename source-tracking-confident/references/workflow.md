# Source Tracking Workflow

This workflow assumes the agent can already access the workbook and can use the `maybeai-sheet` skill for all worksheet writes and styles.

## Scope

This skill does not introduce a new provenance backend. It explains how an agent should:

1. classify source type
2. assign confidence
3. track source freshness
4. run sanity validation
5. write audit worksheets
6. verify the workbook changes

## Step 1: Resolve the audit scope

1. Read `spreadsheet_url`.
2. Prefer `selected_range`.
3. If the user names a worksheet or cells explicitly, use that exact scope.
4. If the request is large and vague, narrow it before writing. Do not silently audit the whole workbook.
5. Skip blank cells and placeholder values such as `N/A`, `NA`, `null`, or `--` unless the cell itself is a meaningful error output that needs auditing.

## Step 2: Collect evidence per cell

For each target cell, capture the minimum viable provenance:

- original worksheet
- original cell
- visible value
- source type
- confidence score
- source date type
- source date
- freshness level
- source link
- section or field locator
- short evidence snippet
- validation status
- validation type
- validation note

Evidence priority:

1. direct API response or direct webpage
2. opened canonical page after search
3. search snippet only
4. model inference

Rules:

- Do not fabricate missing evidence.
- Prefer `effective_date`, then `publish_date`, then `modified_date`.
- If the only known timestamp is when the assistant fetched the data, record it as `retrieved_at` and keep freshness conservative.
- If there is no real source link, keep it blank.
- If multiple evidence items exist for one cell, keep one primary row and add extra rows only when they materially help auditing.
- Keep sanity validation conservative. Use `needs_review` for suspicious values unless there is a hard rule proving `invalid`.

## Step 3: Normalize records

Normalize each cell into the contract table fields:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date_type | source_date | freshness_level | freshness_note | validation_status | validation_type | validation_note | source_link | source_section | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Map score to tier using:

- very_high: `>= 0.9`
- high: `>= 0.75 and < 0.9`
- medium: `>= 0.5 and < 0.75`
- low: `>= 0.25 and < 0.5`
- very_low: `< 0.25`

Map freshness using source-specific judgment:

- `current`: recent enough for the business question
- `aging`: real source, but recency risk is starting to matter
- `stale`: real source, but obviously old for the question context
- `unknown`: no reliable source date available

Do not bind freshness to one fixed day threshold for every domain. A stock quote, market share report, policy document, and annual filing decay at different speeds.

Sanity validation guidance:

- `unit`: detect obvious unit mismatch such as duplicate suffixes, percent stored as whole number, or currency/unit label conflicts
- `range`: detect impossible values such as negative market share or percentage above 100 when the field must be bounded
- `magnitude`: detect values off by obvious powers of 10 or inconsistent with nearby peers
- `outlier`: flag unusually large or small values for review, but do not call them wrong only because they are rare
- `cross_field_consistency`: compare related fields when helpful, such as value vs stated unit or duplicated derived columns

## Step 4: Materialize `<worksheet_name>-source-confident`

Default mode: exact mirror view.

Use exact mirror view by default:

- duplicate the same visible content from the source worksheet
- keep the same cell values
- keep the same row and column positions for the audited scope
- do not insert extra tracking columns into the mirrored grid

Recommended layout:

- worksheet name: `<worksheet_name>-source-confident`
- if that exceeds the sheet-name limit, shorten deterministically, for example `<worksheet_name>-src-conf`
- copied data grid: same coordinates as the audited worksheet/range whenever feasible
- optional legend block: place outside the copied data region, for example to the far right of the used range
- optional metadata block: place outside the copied data region, never above the copied grid if that would shift rows

Color rules:

- very_high: `#b6d7a8`
- high: `#d9ead3`
- medium: `#fff2cc`
- low: `#f9cb9c`
- very_low: `#f4cccc`

Use `batch_set_cell_style` to color the duplicated value cells directly.

Fallback mode: flat confidence table.

Use the flat table when:

- multiple worksheets are involved
- cells are sparse
- the mirror view is impossible or would break the source layout contract

Fallback columns:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date | freshness_level |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Step 5: Materialize `source-tracking`

Always create or refresh a flat audit table with this header:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date_type | source_date | freshness_level | freshness_note | validation_status | validation_type | validation_note | source_link | source_section | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Guidance:

- one row per audited cell is the default
- use multiple rows for one cell only when there are multiple real sources worth preserving
- keep snippets short enough to stay readable in the worksheet
- never put giant raw payloads into one cell

## Step 6: Write with MaybeAI Sheet APIs

Preferred API pattern:

1. `list_worksheets`
2. resolve the worksheet name from `gid` or explicit target
3. if missing, `write_new_worksheet`
4. copy the source values into `<worksheet_name>-source-confident`
5. if existing, `clear_range` or overwrite target ranges
6. `update_range` for exact tabular writes
7. `batch_set_cell_style` for headers and confidence colors
8. optional `set_auto_filter` on the tracking table header
9. `read_sheet` to verify

For formatting, use only the simplified `style` keys supported by `batch_set_cell_style`.

## Step 7: Verify live workbook output

Read back both worksheets and confirm:

1. worksheet exists
2. expected header row exists
3. `<worksheet_name>-source-confident` has the same copied cell values as the source worksheet for the audited scope
4. `<worksheet_name>-source-confident` did not shift the mirrored grid by inserting extra audit rows or columns inside it
5. expected confidence colors were targeted on the duplicated cells
6. source date columns contain real dates when claimed
7. validation columns contain meaningful statuses when sanity review was requested
8. no fake `#fragment` was written

If any of these fail, fix the worksheet before finalizing.

## Step 8: Final response

Keep the final response short:

- audited scope
- created worksheets
- count by confidence tier
- count by source type
- count by freshness level
- count by validation status
- verification result
- any cells left as `llm/very_low`
