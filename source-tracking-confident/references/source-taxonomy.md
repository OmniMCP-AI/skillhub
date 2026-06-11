# Source Type And Confidence Taxonomy

Use this file only when the classification is not obvious from the request or evidence.

## Source types

### `web`

Use when the value is supported by a directly opened webpage, PDF page, document page, or canonical article URL.

Typical evidence:

- canonical page URL
- section heading or paragraph locator
- short supporting snippet

### `api`

Use when the value comes from a structured API, database response, or tool result with stable fields.

Typical evidence:

- endpoint or system URL
- response field path such as `data.items[0].price`
- response excerpt

### `tool`

Use when the value is best attributed to a specific tool execution and the tool output is the closest stable provenance surface the assistant can inspect.

Use `tool` when:

- the tool output is available but its deeper upstream source is not recoverable
- the tool is a compound retriever or transformer
- the provenance needs to point to a concrete tool step first

Typical evidence:

- tool name
- tool-call id or step number
- output path or JSON locator
- short output excerpt

### `file`

Use when the value comes from an uploaded file, retrieved file, spreadsheet attachment, local document, or parsed PDF/docx section.

Typical evidence:

- file name or file path
- document URL when real
- page, sheet, section, or paragraph locator
- extracted snippet

### `search`

Use when the value is only supported by search results or search snippets, not by the opened canonical source page.

Rules:

- `search` must not be `high`
- prefer upgrading `search` to `web` only after the underlying page is opened and verified

### `llm`

Use when the value is model-derived, guessed, summarized without stable evidence, or otherwise unsupported.

Rules:

- default to `low`
- keep `source_link` blank unless a real link exists
- use `note` to explain the uncertainty

### `mixed`

Use when one cell materially combines more than one source type and you cannot fairly collapse it into a single primary type.

Example:

- a web page value normalized and then completed by an API fallback

### `user`

Use when the value was explicitly provided by the user.

## Confidence scoring guidance

### High: `>= 0.8`

Use when all of these are true:

- direct evidence exists
- the evidence matches the cell value closely
- the source is stable enough to cite
- a reviewer could reproduce the result quickly

Examples:

- exact value visible on a webpage and linked
- exact API field response
- direct quote or direct numeric field

### Medium: `>= 0.4` and `< 0.8`

Use when evidence exists but is partial, transformed, or weaker.

Examples:

- search snippet only
- source page supports the claim indirectly
- multiple plausible matches required manual interpretation
- normalized or lightly transformed value with incomplete trace

### Low: `< 0.4`

Use when evidence is missing, weak, conflicting, or model-derived.

Examples:

- pure LLM inference
- no source URL
- paragraph or API field cannot be identified
- claim was copied from a prior answer without proof

## Tie-break rules

1. Prefer the lower confidence tier when in doubt.
2. Prefer `web` or `api` over `search` only after verification.
3. Prefer `file` or `tool` over `llm` when the assistant run clearly shows a file read or tool output.
4. Prefer `llm` over pretending there is a real source.
5. If the cell has one strong source and one weak source, keep the strongest real source as primary and mention the weaker one in `note` or extra rows.
