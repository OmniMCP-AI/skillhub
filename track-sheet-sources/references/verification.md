# Track Sheet Sources Verification

Use this checklist to verify that the skill is doing real provenance capture.

## Acceptance criteria

### A. Worksheet existence

- `source-tracking` exists

### B. Tracking table quality

Verify:

- the header row matches the contract
- each audited cell has at least one row
- blank and placeholder cells were skipped unless they were true error outputs
- `source_type` is never blank
- `source_link` is blank rather than fabricated when missing
- `source_section` carries paragraph, heading, or field locator when available
- `source_date_type` and `source_date` are present when the source exposes them

### C. Hallucination control

Verify:

- search-only evidence stayed `search` unless the page was actually opened
- unsupported rows stayed `llm`
- no fake URL fragments were created
- no fake source dates were written

### D. Read-back verification

After writing, read `source-tracking` back and confirm:

- header cells are present
- row counts match the intended write
- representative audit rows match expected values

## Minimal expected `source-tracking` sample

| worksheet_name | cell | value | source_type | source_link | source_section | source_date_type | source_date | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Sheet1` | `B2` | `123` | `api` | `https://api.example.com/orders/1` | `$.data.order_id` | `effective_date` | `2026-06-10` | `order_id = 123` | `api call` | `` |
| `Sheet1` | `C2` | `ACME` | `web` | `https://example.com/product/acme` | `Specs > Brand` | `publish_date` | `2025-11-03` | `Brand: ACME` | `opened page` | `normalized casing` |
| `Sheet1` | `D2` | `2025 estimate` | `llm` | `` | `` | `` | `` | `` | `llm synthesis` | `no direct source found` |
