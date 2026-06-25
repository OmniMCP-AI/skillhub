# document-ingestion adapter contract for FinClaw

This reference records the integration boundary for `data-reporting/document-ingestion` inside the existing FinClaw product flow.

## Position

Keep the original FinClaw entry and main chain:

```text
data-reporting/finclaw-financial-analysis-runner
  -> data intake / user-provided files
  -> data validation
  -> financial-statements/finclaw-three-statement-foundation
  -> comprehensive-finance/finance-business-analysis
  -> data-reporting/bi-analysis
  -> global/maybeai-sheet
  -> follow-up support
```

`data-reporting/document-ingestion` is only an optional adapter between data intake and the three-statement foundation:

```text
data intake
  -> [optional] document-ingestion for irregular files
  -> FinClaw three-statement-foundation
```

## Trigger rules

Directly continue the original FinClaw flow when the input is already structured and readable:

- `.xlsx`
- `.xlsm`
- `.csv`
- `.tsv`
- readable MaybeAI Sheet structured worksheets

Run `data-reporting/document-ingestion` first when the input is irregular or may need format adaptation:

- `.xls`
- `.docx`
- text-layer PDF
- ZIP bundles
- multi-file folders / bundles
- images
- scanned PDFs

## Handoff payload

Only pass input-preparation artifacts forward:

- `extracted_tables`
- `extracted_text`
- `source_manifest`
- `issues`

These artifacts help the original FinClaw chain find and normalize inputs; they are not finance conclusions.

## Blocking outcomes

If `issues` includes any of these codes, stop before generating a formal financial report:

- `requires_ocr`
- `missing_dependency`
- `unsupported_format`

Tell the user what is needed next: OCR, file conversion, dependency installation, or missing files.

## Non-replacement rules

`document-ingestion` must not:

- generate report conclusions;
- replace `FinClaw three-statement-foundation`;
- replace `finance-business-analysis`;
- replace `bi-analysis`;
- change the final MaybeAI Sheet report structure;
- become a new product entry or a new primary flow.

## Pitfall from session correction

Do not respond to this integration by inventing a new fixed workflow such as “when user asks for a company report, always do X.” The durable product behavior is an incremental update to the existing runner: keep the old entry, keep the old chain, and insert document-ingestion only when file type/structure requires it.
