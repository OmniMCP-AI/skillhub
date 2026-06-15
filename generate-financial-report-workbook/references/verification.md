# Verification

## Workbook Verification

Verify:

- workbook was created or uploaded successfully
- expected business worksheets exist
- row 1 headers read back cleanly, without `_col_*` caused by decorative title rows
- demo/synthetic data is visibly labeled when used
- no visible `source-tracking`, `confidence-assessment`, `SourceMeta`, `底稿-SourceMeta`, or `<worksheet>-source-confident` sheet exists or was updated in the product workbook
- visible metadata worksheets in a product workbook are not evidence of successful tracking; only play-be sidecar metadata plus feature config count as success

## Sidecar Metadata Verification

For each worksheet with tracked data:

1. `cell-metadata/batch-upsert` returns the intended row count
2. `provenance-feature/upsert` returns:
   - `source_tracking_enabled=true`
   - `source_confidence_enabled=true`
   - `capture_mode=write_time`
3. `provenance-feature/detail` returns the same config for the same `doc_id` and `gid` after document permission checks pass
4. `cell-metadata/query` returns representative sample cells
5. sample metadata is not duplicated by writer user; the effective identity is `doc_id + gid + row + col`

## Source Distribution Verification

Reject or fix metadata when:

- all cells are `source_type=tool` because a workbook writer was used
- synthetic/demo values are not represented as `source_type=llm` plus `source_refs[].upstream_source_type=synthetic`
- calculation/formula cells use row-level `source_type=formula`
- search-only evidence is upgraded to `web` without opening/citing the canonical page

## Confidence Distribution Verification

Reject or fix metadata when:

- all cells have `confidence_level=2` by default
- confidence uses 0-100 instead of 1-5
- synthetic disclaimers are scored the same as synthetic financial assumptions
- formula/reconciliation cells are not distinguished from assumptions

For a synthetic/demo finance workbook, a plausible distribution often includes:

- `4`: visible demo disclaimers, workbook metadata, true report-scope statements
- `3`: verified formulas, ratios, reconciled totals, sanity-checked benchmark applications
- `2`: synthetic assumptions and management interpretations
- `1`: unsupported real-company factual claims, if any

## Final Response Verification

The final response should mention:

- workbook URL/path
- whether data is real, public benchmark, synthetic, or mixed
- sidecar metadata row count
- source distribution
- confidence distribution
- limitations

Do not dump raw metadata rows into the user response.

## Legacy Worksheet Cleanup Signal

If the product workbook already contains `source-tracking`, `confidence-assessment`, `SourceMeta`, `底稿-SourceMeta`, or `<worksheet>-source-confident` sheets from an older run:

- do not add new rows to them
- do not create additional mirror sheets
- write or repair play-be sidecar metadata for the business worksheets
- mention that the visible metadata worksheets are legacy artifacts and should be removed or hidden by a separate cleanup action if the user wants a cleaner workbook
