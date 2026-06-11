# Source Tracking Verification

Use this checklist to verify that the skill is doing a real provenance audit instead of writing decorative worksheets.

## Example target

- workbook: `https://www.maybe.ai/docs/spreadsheets/d/6a2a3df5a39b53dae3c9d077?gid=0`
- expected new worksheets:
  - `Supply Chain Latest-source-confident`
  - `source-tracking`

If the target workbook is sensitive, copy it first and verify on the copy.

## Acceptance criteria

### A. Worksheet existence

- `<worksheet_name>-source-confident` exists
- `source-tracking` exists

### B. Confidence illustration

In `<worksheet_name>-source-confident`, verify:

- the duplicated sheet/range has the same visible values as the source worksheet
- the duplicated sheet/range keeps the same row and column structure for the audited scope
- at least one confidence color is applied when matching data exists
- cells are colored by confidence tier, not by source type
- any legend or metadata block is outside the mirrored data region

### C. Tracking table quality

In `source-tracking`, verify:

- the header row exactly matches the contract
- each audited cell has at least one row
- blank and placeholder cells were skipped unless they were true error outputs
- `source_type` is never blank
- `confidence_level` is never blank
- `source_date_type` and `source_date` are present when the source exposes them
- `freshness_level` is never blank when a real source row exists
- `validation_status` is present when sanity review was requested
- outliers are marked `needs_review` rather than automatically `invalid` unless a hard rule is violated
- `source_link` is blank rather than fabricated when missing
- `source_section` carries paragraph, heading, or field locator when available

### D. Hallucination control

Verify:

- unsupported claims were marked `llm` and `very_low`
- search-only evidence was not marked `high`
- no fake URL fragments were created
- old sources were not silently treated as fresh
- obvious unit or magnitude problems were surfaced in validation fields

### E. Read-back verification

After writing, read both worksheets back and confirm:

- header cells are present
- row counts match the intended write
- representative audit rows match expected values

## Suggested live verification sequence

1. `list_worksheets`
2. `read_sheet` for the target range
3. write or refresh `<worksheet_name>-source-confident`
4. write or refresh `source-tracking`
5. `batch_set_cell_style` for header and confidence colors
6. `read_sheet` on `<worksheet_name>-source-confident`
7. `read_sheet` on `source-tracking`

## Minimal expected `source-tracking` sample

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_link | source_section | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Sheet1` | `B2` | `123` | `api` | `very_high` | `0.92` | `https://api.example.com/orders/1` | `$.data.order_id` | `order_id = 123` | `api call` | `` |
| `Sheet1` | `C2` | `ACME` | `web` | `medium` | `0.63` | `https://example.com/product/acme` | `Specs > Brand` | `Brand: ACME` | `opened page` | `normalized casing` |
| `Sheet1` | `D2` | `2025 estimate` | `llm` | `very_low` | `0.20` | `` | `` | `` | `llm synthesis` | `no direct source found` |

Expected freshness columns for the same rows:

| cell | source_date_type | source_date | freshness_level | freshness_note |
| --- | --- | --- | --- | --- |
| `B2` | `effective_date` | `2026-06-10` | `current` | `same-day API snapshot` |
| `C2` | `publish_date` | `2025-11-03` | `aging` | `web source is real but several months old` |
| `D2` | `` | `` | `unknown` | `no real source date available` |

Expected sanity-validation columns for the same rows:

| cell | validation_status | validation_type | validation_note |
| --- | --- | --- | --- |
| `B2` | `ok` | `range` | `value fits expected field range` |
| `C2` | `needs_review` | `outlier` | `value is unusual relative to nearby peers but not provably wrong` |
| `D2` | `unknown` | `manual_review` | `not enough reliable source context to validate` |

## Minimal expected `<worksheet_name>-source-confident` behavior

| check | expectation |
| --- | --- |
| worksheet name | `Supply Chain Latest-source-confident` |
| duplicated values | same as `Supply Chain Latest` for the audited scope |
| row/column positions | same as source sheet for the audited scope |
| very_high color | `#b6d7a8` |
| high color | `#d9ead3` |
| medium color | `#fff2cc` |
| low color | `#f9cb9c` |
| very_low color | `#f4cccc` |
