# Track Sheet Sources Taxonomy

Use this file only when source classification is not obvious from the evidence.

## Source types

### `web`

Use when the value is supported by a directly opened webpage, PDF page, document page, or canonical article URL.

### `api`

Use when the value comes from a structured API, database response, or tool result with stable fields.

### `tool`

Use when the tool output is the closest stable provenance surface the assistant can inspect and the deeper upstream source is not recoverable.

### `file`

Use when the value comes from an uploaded file, retrieved file, spreadsheet attachment, local document, or parsed PDF/docx section.

### `search`

Use when the value is supported only by search snippets or search results, not by an opened canonical page.

### `llm`

Use when the value is model-derived, guessed, summarized without stable evidence, or otherwise unsupported.

### `mixed`

Use when one cell materially combines more than one source type and you cannot fairly collapse it into a single primary type.

### `user`

Use when the value was explicitly provided by the user.

## Tie-break rules

1. Prefer `web` or `api` over `search` only after verification.
2. Prefer `file` or `tool` over `llm` when the assistant run clearly shows a file read or tool output.
3. Prefer `llm` over pretending there is a real source.
4. If the cell has one strong source and one weak source, keep the strongest real source as primary and mention the weaker one in `note` or extra rows.
