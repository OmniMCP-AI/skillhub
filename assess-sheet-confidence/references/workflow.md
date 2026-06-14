# Assess Sheet Confidence Workflow

This workflow assumes the agent can access the workbook and can use the `maybeai-sheet` skill for worksheet reads, writes, and styles.

## Scope

This skill explains how an agent should:

1. resolve the assessment scope
2. derive confidence inputs
3. score confidence, freshness, and sanity
4. materialize sidecar metadata or fallback `<worksheet_name>-source-confident`
5. optionally enrich `source-tracking` only in standalone mode
6. verify the metadata/write result

## Step 1: Resolve the assessment scope

1. Read `spreadsheet_url`.
2. Prefer `selected_range`.
3. If the user names a worksheet or cells explicitly, use that exact scope.
4. If the request is large and vague, narrow it before writing.
5. Skip blank cells and placeholder values unless they are meaningful error outputs.

## Step 2: Gather confidence inputs

Prefer these sources in order:

1. existing `source-tracking`
2. session history and tool-call records
3. attached citations or opened sources
4. direct sheet values and neighboring context

For each target cell, capture:

- visible value
- source type when known
- available source date
- provenance strength
- domain context needed for sanity checks

## Step 3: Score the row

### Confidence

Map evidence quality to sidecar numeric levels and standalone text tiers:

- `5` / `very_high`: direct, reproducible evidence with tight value match
- `4` / `high`: good evidence, minor transformation or recency concern
- `3` / `medium`: partial evidence, inferred mapping, or weaker trace
- `2` / `low`: weak evidence, estimated mapping, or strong ambiguity
- `1` / `very_low`: model-derived or unsupported

### Freshness

Use source-specific judgment:

- `current`: recent enough for the business question
- `aging`: real source, but recency risk is starting to matter
- `stale`: real source, but obviously old for this question
- `unknown`: no reliable source date

### Sanity

Use conservative checks:

- `unit`: duplicate suffixes, unit conflicts, or mislabeled scales
- `range`: impossible bounded values
- `magnitude`: obvious powers-of-10 mistakes or peer-scale mismatch
- `outlier`: unusual values worth review, but not automatically wrong
- `cross_field_consistency`: mismatch across related fields

## Step 4: Materialize sidecar metadata or fallback mirror

### Preferred: `metadata_output=sidecar`

Use this mode when the assistant created or is creating the product worksheet/workbook.

Required behavior:

- write the worksheet/workbook first using the normal MaybeAI Sheet path
- do not create `<worksheet_name>-source-confident`
- do not create `source-tracking`
- do not change workbook styles
- build normalized `cell_metadata[]` with `doc_id`, `gid`, `cell`, `row`, `col`, `value_hash`, `confidence_level`, `confidence_score`, and `confidence_reason`
- include `source_type` and `source_refs` only when backed by real provenance; do not fabricate sources to justify a score
- after the worksheet/workbook write succeeds, call play-be cell metadata batch-upsert with `X-Internal-Token`, `X-User-Id`, and optional `X-User-Email`
- call `provenance-feature/upsert` for `doc_id + gid` with source confidence enabled and the same internal headers
- report partial completion if workbook creation succeeds but metadata upsert fails

Default product skip rules:

- skip row 1 as header
- skip column A as id/label column
- include them only when the caller explicitly marks them as data cells

### Fallback: `<worksheet_name>-source-confident`

Standalone fallback behavior is exact mirror view:

- duplicate the same visible content from the source worksheet
- keep the same row and column positions
- do not insert tracking columns or helper blocks
- apply confidence colors directly to the duplicated cells
- if copying coerces visible strings into raw numbers, reapply formats so the mirror still looks like the source

Color mapping:

- `very_high`: `#b6d7a8`
- `high`: `#d9ead3`
- `medium`: `#fff2cc`
- `low`: `#f9cb9c`
- `very_low`: `#f4cccc`

These colors are internal style mappings only. Do not write raw hex strings into worksheet cells.

## Step 5: Enrich `source-tracking` when useful in standalone mode

If `source-tracking` exists:

- preserve the provenance columns
- add or refresh:
  - `confidence_level`
  - `confidence_score`
  - `freshness_level`
  - `freshness_note`
  - `validation_status`
  - `validation_type`
  - `validation_note`

If `source-tracking` is missing and the user only asked for confidence coloring, do not create a fake provenance table unless the user explicitly asked for one.

## Step 6: Verify output

For sidecar mode, confirm:

1. workbook or worksheet creation succeeded before metadata upsert
2. sidecar rows equal the intended assessed data cells after header/first-column skip rules
3. every row has `doc_id`, `gid`, `cell`, `row`, `col`, `value_hash`, `confidence_level`, and `confidence_reason`
4. every `confidence_level` is an integer from `1` through `5`
5. `source_refs` are real evidence only; unsupported rows use `source_refs=[]` and low confidence rather than fake sources
6. `provenance-feature/upsert` enabled source confidence for the target `doc_id + gid`
7. no helper worksheet, style change, or visible cell change was made for metadata

For standalone mirror mode:

Read back the affected worksheets and confirm:

1. the mirror worksheet exists
2. visible values match the source for the audited scope
3. row and column positions match the source
4. visible formats still look correct
5. confidence colors were applied to the intended cells
6. no helper text or raw hex strings were written into visible cells
7. if `source-tracking` was enriched, the expected assessment columns are present

If any of these fail, fix the worksheet before finalizing.

## Step 7: Final response

Keep the final response short:

- audited scope
- metadata output mode
- created or updated worksheets, if standalone fallback was used
- counts by confidence tier
- counts by freshness level
- counts by validation status
- verification result
