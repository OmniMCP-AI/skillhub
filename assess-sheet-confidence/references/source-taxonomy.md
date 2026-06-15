# Source Quality And Confidence Rubric

Use this file only when confidence depends on source quality or ambiguous provenance.

## Source quality hints

### `api`

Usually strongest when:

- the response field is stable and directly matches the cell value
- the timestamp is known

### `database`

Usually strongest when:

- the query/table context is known
- the field and row mapping directly match the cell value
- the extraction timestamp or data effective date is known

### `web`

Usually strong when:

- the canonical page is opened
- the value is directly visible and citable

### `file`

Usually strong when:

- the file section, page, or sheet is known
- the extracted value is exact

### `document`

Usually strong when:

- the managed document id, section, heading, or page locator is known
- the quoted or extracted value directly matches the cell value

### `multimedia`

Usually medium to strong when:

- the transcript, OCR, frame, or timestamp locator is recorded
- the extraction method is reproducible
- confidence should be lowered when OCR/transcription quality is uncertain

### `search`

Weaker by default:

- do not treat search snippets as direct proof
- upgrade to `web` only after opening the real page

### `llm`

Weakest by default:

- use `very_low` for unsupported real-world factual claims
- do not automatically mark every synthetic/demo workbook cell as `low`; score the claim being made

For synthetic/demo workbooks, separate these dimensions:

- real-world factual accuracy: usually low or very low unless backed by web/file/api evidence
- disclosure accuracy: can be high when the sheet clearly says "demo/synthetic/not real data"
- computational consistency: can be medium or high when formulas, ratios, and cross-sheet checks are reproducible
- industry plausibility: can be low or medium when assumptions match documented industry ranges, but no exact real-company evidence exists

### `tool`

Tool output is not automatically high or low confidence. Score the upstream source and the tool role:

- `workbook_writer`: does not raise confidence by itself
- `calculator`: can support medium/high computational consistency if inputs are known and formulas are reproducible
- `extractor`: confidence depends on the extracted source quality
- `searcher`: weak until a canonical page is opened
- `api_client` or `database_client`: can be high/very_high if field mapping is direct and timestamped

## Confidence tier guidance

### `very_high`

Use when:

- direct evidence exists
- the evidence matches the cell value tightly
- a reviewer could reproduce the result quickly

### `high`

Use when:

- evidence is good but there is minor transformation, recency risk, or small ambiguity
- the claim is a disclosure or metadata statement that is directly true of the generated workbook, such as "this is synthetic/demo data"

### `medium`

Use when:

- evidence exists but is partial, inferred, or weaker than direct proof
- a generated workbook value is computationally reproducible from known synthetic inputs and passes cross-sheet sanity checks
- an industry assumption is plausible and sanity-checked, but not backed by a direct real-company source

### `low`

Use when:

- the mapping is estimated, ambiguous, or only weakly supported
- a synthetic/demo numeric assumption is plausible but not externally sourced
- a business interpretation references real companies or market behavior without direct evidence

### `very_low`

Use when:

- the value is model-derived
- no stable evidence exists
- the trace is too weak to support a stronger grade

## Tie-break rules

1. Prefer the lower confidence tier when in doubt.
2. Prefer `very_low` over pretending the value is supported.
3. Prefer `web` or `api` over `search` only after verification.
4. Treat stale but real data as potentially `high` or `medium` confidence with separate freshness risk, not automatically low confidence.
5. Do not produce a single uniform confidence level for an entire workbook unless all cells truly share the same claim type and evidence quality.
6. For synthetic/demo workbooks, create a varied distribution that reflects disclosure, calculation, assumptions, and unsupported real-world claims.

## Synthetic/demo workbook rubric

Use this rubric when the task asks to "simulate", "mock", "demo", or otherwise generate a workbook without real source data.

| cell class | source_type | recommended confidence | validation_status | reason |
| --- | --- | --- | --- | --- |
| explicit demo/synthetic disclaimer requested by user | `user` or `llm` | `4` high | `ok` | disclosure is true and visible in workbook |
| workbook metadata, sheet names, generated date, known output path | `tool` in refs, upstream `llm` | `4` high | `ok` | generated artifact property is verifiable |
| formulas, ratios, cross-sheet totals from synthetic inputs | upstream source of inputs, often `llm` | `3` medium | `ok` or `needs_review` | calculation is reproducible but inputs are synthetic |
| synthetic financial assumptions and forecast numbers | `llm` with `upstream_source_type=synthetic` | `2` low, sometimes `3` if sanity-checked | `needs_review` | plausible but not real-world evidence |
| industry structure assumptions without search/file evidence | `llm` or `search` if snippet-only | `2` low | `needs_review` | not directly sourced |
| claims about real companies' exact facts without citation | `llm` | `1` very_low | `needs_review` or `invalid` | unsupported real-world claim |
| real values copied from annual report, uploaded file, API, or opened page | `file`/`api`/`web` | `4` or `5` | `ok` | direct evidence exists |

If the whole workbook was generated by a script, do not assign all cells `source_type=tool` and `confidence_level=2`. The script is a delivery method, not the evidence source.
