# Source And Confidence Policy

## Source Type Policy

Row-level `source_type` must describe the upstream data source, not the execution tool.

Allowed row-level values:

- `database`
- `api`
- `tool`
- `file`
- `document`
- `web`
- `search`
- `multimedia`
- `llm`
- `mixed`
- `user`
- `unknown`

Do not use unsupported row-level values such as `synthetic` or `formula`.

## Tool Is Not The Source

Tools are execution methods. Preserve them in `source_refs[]`:

```json
{
  "source_type": "tool",
  "tool_name": "openpyxl",
  "tool_role": "workbook_writer",
  "upstream_source_type": "synthetic",
  "section": "workbook generation script"
}
```

Examples:

| situation | row-level `source_type` | tool evidence |
| --- | --- | --- |
| `openpyxl` wrote synthetic assumptions | `llm` | `tool_role=workbook_writer`, `upstream_source_type=synthetic` |
| Akshare returned finance data | `api` | `tool_role=api_client`, `tool_name=akshare` |
| Tavily answer from opened/cited page | `web` if page opened, otherwise `search` | `tool_role=searcher` |
| PDF annual report parsed by script | `file` or `document` | `tool_role=extractor` |
| formula ratio computed from sheet values | source type of inputs | `tool_role=calculator` |

Use `source_type=tool` only when the tool output itself is the only recoverable provenance surface and no upstream source can be identified.

## Confidence Scale

Use `confidence_level` integer `1` through `5` only.

| level | label | default meaning |
| --- | --- | --- |
| `5` | very high | direct reproducible evidence with tight value match |
| `4` | high | good evidence or true generated-workbook disclosure |
| `3` | medium | reproducible calculation or sanity-checked benchmark/synthetic value |
| `2` | low | plausible synthetic assumption or weak/indirect support |
| `1` | very low | unsupported real-world factual claim |

Do not use a 0-100 confidence scale in play-be sidecar metadata.

## Synthetic/Demo Workbook Scoring

When the workbook is simulated/demo:

| cell class | source_type | confidence_level | validation_status |
| --- | --- | --- | --- |
| visible disclaimer that data is demo/synthetic | `user` or `llm` | `4` | `ok` |
| workbook metadata, generated date/path, report scope | `llm` or `user` | `4` | `ok` |
| formulas, ratios, and reconciled totals from known synthetic inputs | upstream source, often `llm` | `3` | `ok` if checked |
| synthetic financial assumptions and business interpretations | `llm` | `2` | `needs_review` |
| unsupported facts about real companies | `llm` | `1` | `needs_review` or `invalid` |
| copied values from annual report/API/web/file | `web`/`api`/`file`/`document` | `4` or `5` | `ok` |

## Public Finance Workbook Scoring

When public data is used:

- Akshare finance fields with direct mapping: `source_type=api`, confidence `4` or `5`
- opened public annual report/page: `source_type=web` or `document`, confidence `4` or `5`
- Tavily/Serper answer without opening canonical page: `source_type=search`, confidence usually `2` or `3`
- industry range calibrated from multiple sources but applied to a simulated company: `source_type=mixed` or `llm`, confidence `2` or `3`

## Anti-Regression Checks

Reject or revise metadata when:

- all or most cells are `source_type=tool` merely because a script generated the workbook
- all or most cells are `confidence_level=2` without claim-type justification
- sidecar metadata uses unsupported source types such as `synthetic` or `formula`
- confidence is stored as 0-100 instead of 1-5
- visible workbook helper sheets are created without explicit user request
