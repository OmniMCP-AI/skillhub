# Source Quality And Confidence Rubric

Use this file only when confidence depends on source quality or ambiguous provenance.

## Source quality hints

### `api`

Usually strongest when:

- the response field is stable and directly matches the cell value
- the timestamp is known

### `web`

Usually strong when:

- the canonical page is opened
- the value is directly visible and citable

### `file`

Usually strong when:

- the file section, page, or sheet is known
- the extracted value is exact

### `search`

Weaker by default:

- do not treat search snippets as direct proof
- upgrade to `web` only after opening the real page

### `llm`

Weakest by default:

- use `very_low` unless there is better direct evidence

## Confidence tier guidance

### `very_high`

Use when:

- direct evidence exists
- the evidence matches the cell value tightly
- a reviewer could reproduce the result quickly

### `high`

Use when:

- evidence is good but there is minor transformation, recency risk, or small ambiguity

### `medium`

Use when:

- evidence exists but is partial, inferred, or weaker than direct proof

### `low`

Use when:

- the mapping is estimated, ambiguous, or only weakly supported

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
