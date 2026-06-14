# Track Sheet Sources Workflow

This workflow assumes the agent can already access the workbook and can use the `maybeai-sheet` skill for worksheet reads and writes.

## Scope

This skill supports play-be sidecar metadata in product write-time flows and keeps the standalone `source-tracking` worksheet as a fallback. It explains how an agent should:

1. resolve the audit scope
2. reconstruct provenance per cell
3. normalize source records
4. write sidecar metadata or fallback `source-tracking`
5. verify the metadata/write result

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

For `metadata_output=sidecar`, also normalize each cell into `cell_metadata[]` with:

- `doc_id`, `gid`, `worksheet_name`
- `cell`, `row`, `col`
- `value_preview`, `value_hash`
- `source_type`, `source_refs`
- optional `source_date_type`, `source_date`, `evidence_excerpt`, `retrieval_method`, `note`

Skip header row 1 and column A by default for product-generated sidecar metadata unless the caller explicitly includes them as data cells.

## Step 4: Materialize sidecar metadata or fallback worksheet

### Preferred: `metadata_output=sidecar`

Use this mode when the assistant created or is creating the product worksheet/workbook.

Required behavior:

- write the worksheet/workbook first using the normal MaybeAI Sheet path
- do not create `source-tracking`
- do not change workbook styles
- after the worksheet/workbook write succeeds, call play-be cell metadata batch-upsert with `cell_metadata[]`
- call `provenance-feature/upsert` for `doc_id + gid` with source tracking enabled
- report partial completion if workbook creation succeeds but metadata upsert fails

### Fallback: standalone worksheet

Create or refresh a flat audit table only when sidecar output is unavailable or explicitly not requested.

Preferred write behavior:

- if the sheet does not exist, create it with the base header
- if the sheet exists and already has extra columns, preserve those columns when feasible
- update or overwrite the audited row set without deleting unrelated rows unless the user explicitly asked for a full rebuild

## Step 5: Write with MaybeAI Sheet APIs

Preferred API pattern for sidecar mode:

1. create or update the workbook/worksheet
2. capture the returned `doc_id`, `gid`, and worksheet name
3. build normalized `cell_metadata[]`
4. call play-be batch-upsert for cell metadata with `X-Internal-Token`, `X-User-Id`, and optional `X-User-Email`
5. call play-be `provenance-feature/upsert` with the same internal headers
6. query or otherwise verify sidecar row counts

Preferred API pattern for standalone worksheet mode:

1. `list_worksheets`
2. `read_sheet` for the target scope
3. if `source-tracking` is missing, `write_new_worksheet`
4. otherwise `update_range` for exact table writes
5. `batch_set_cell_style` for header emphasis when useful
6. `read_sheet` to verify

## Step 6: Verify output

For sidecar mode, confirm:

1. workbook or worksheet creation succeeded before metadata upsert
2. sidecar rows equal the intended audited data cells
3. default product skip rules excluded header row 1 and column A unless explicitly overridden
4. every row has `doc_id`, `gid`, `cell`, `row`, `col`, `source_type`, `source_refs`, and `value_hash`
5. `source_refs` contain only real evidence and no fabricated URLs, fragments, field paths, or dates
6. `provenance-feature/upsert` enabled source tracking for the target `doc_id + gid`

For standalone worksheet mode:

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
- metadata output mode
- created worksheets, if standalone fallback was used
- row count written to sidecar or `source-tracking`
- count by source type
- date coverage
- verification result
