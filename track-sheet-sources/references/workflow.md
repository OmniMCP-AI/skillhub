# Track Sheet Sources Workflow

This workflow assumes the agent can already access the workbook and can use the `maybeai-sheet` skill for worksheet reads and writes.

## Scope

This skill does not introduce a new provenance backend. It explains how an agent should:

1. resolve the audit scope
2. reconstruct provenance per cell
3. normalize source records
4. write `source-tracking`
5. verify the workbook changes

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
- source link
- section or field locator
- source date type
- source date
- short evidence snippet
- retrieval method
- note

Evidence priority:

1. direct API response or direct webpage
2. opened canonical page after search
3. search snippet only
4. model inference

Rules:

- Do not fabricate missing evidence.
- Prefer `effective_date`, then `publish_date`, then `modified_date`.
- If the only known timestamp is when the assistant fetched the data, record it as `retrieved_at`.
- If there is no real source link, keep it blank.
- If multiple evidence items exist for one cell, keep one primary row and add extra rows only when they materially help auditing.

## Step 3: Normalize records

Normalize each cell into the base `source-tracking` fields:

| worksheet_name | cell | value | source_type | source_link | source_section | source_date_type | source_date | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Source classification guidance:

- `api`: direct API response or API-backed tool output
- `tool`: deterministic tool output not better classified as API or file
- `file`: uploaded or retrieved file content
- `web`: opened canonical webpage or PDF
- `search`: search snippet only
- `llm`: model synthesis without direct evidence
- `mixed`: multiple real upstream sources
- `user`: explicitly provided by the user

## Step 4: Materialize `source-tracking`

Always create or refresh a flat audit table.

Preferred write behavior:

- if the sheet does not exist, create it with the base header
- if the sheet exists and already has extra columns, preserve those columns when feasible
- update or overwrite the audited row set without deleting unrelated rows unless the user explicitly asked for a full rebuild

## Step 5: Write with MaybeAI Sheet APIs

Preferred API pattern:

1. `list_worksheets`
2. `read_sheet` for the target scope
3. if `source-tracking` is missing, `write_new_worksheet`
4. otherwise `update_range` for exact table writes
5. `batch_set_cell_style` for header emphasis when useful
6. `read_sheet` to verify

## Step 6: Verify live workbook output

Read back `source-tracking` and confirm:

1. worksheet exists
2. expected header row exists
3. representative audit rows match expected values
4. no fake `#fragment` was written
5. placeholder cells were skipped unless they were true error outputs

If any of these fail, fix the worksheet before finalizing.

## Step 7: Final response

Keep the final response short:

- audited scope
- created worksheets
- row count written to `source-tracking`
- count by source type
- date coverage
- verification result
