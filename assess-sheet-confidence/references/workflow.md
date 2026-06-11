# Assess Sheet Confidence Workflow

This workflow assumes the agent can access the workbook and can use the `maybeai-sheet` skill for worksheet reads, writes, and styles.

## Scope

This skill explains how an agent should:

1. resolve the assessment scope
2. derive confidence inputs
3. score confidence, freshness, and sanity
4. materialize `<worksheet_name>-source-confident`
5. optionally enrich `source-tracking`
6. verify the workbook changes

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

Map evidence quality to:

- `very_high`: direct, reproducible evidence with tight value match
- `high`: good evidence, minor transformation or recency concern
- `medium`: partial evidence, inferred mapping, or weaker trace
- `low`: weak evidence, estimated mapping, or strong ambiguity
- `very_low`: model-derived or unsupported

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

## Step 4: Materialize `<worksheet_name>-source-confident`

Default mode is exact mirror view:

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

## Step 5: Enrich `source-tracking` when useful

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

## Step 6: Verify live workbook output

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
- created or updated worksheets
- counts by confidence tier
- counts by freshness level
- counts by validation status
- verification result
