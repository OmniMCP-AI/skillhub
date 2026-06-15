---
name: generate-financial-report-workbook
description: Orchestrates creation of financial analysis Excel or MaybeAI Sheet workbooks, especially Chinese company/industry reports, then automatically writes source tracking and confidence metadata to play-be sidecar. Use when the user asks to generate a finance report workbook, financial analysis Excel, management review spreadsheet, boss review report, KPI/three-statement workbook, or public-company/industry analysis Excel. This workflow keeps the user prompt simple and enforces source/confidence sidecar behavior.
metadata:
  openclaw:
    requires:
      env:
        - MAYBEAI_API_TOKEN
    optional:
      env:
        - SERPER_API_KEY
        - TAVILY_API_KEY
      pip:
        - akshare
        - pandas
        - openpyxl
    primaryEnv: MAYBEAI_API_TOKEN
---

# Generate Financial Report Workbook

Use this workflow skill when the user asks for a financial analysis Excel/workbook. The user should only need to state the business goal, for example:

```text
请生成一份头部快消护肤品企业财务分析报告 Excel，参考珀莱雅、韩束的分析颗粒度。
```

Do not require the user to mention source tracking, confidence metadata, tool selection, Akshare, Tavily, Serper, or play-be sidecar details.

## Core Rule

The product default is **sidecar metadata only**:

- create or upload the workbook normally
- do not create visible `source-tracking`, `SourceMeta`, `底稿-SourceMeta`, `<worksheet>-source-confident`, or confidence mirror worksheets
- after workbook creation, write source/confidence metadata to play-be:
  - `POST http://play-be.omnimcp.ai/api/v1/sheet/cell-metadata/batch-upsert`
  - `POST http://play-be.omnimcp.ai/api/v1/sheet/provenance-feature/upsert`
- use `confidence_level` integer `1` through `5`
- use only backend-supported row-level source types: `database`, `api`, `tool`, `file`, `document`, `web`, `search`, `multimedia`, `llm`, `mixed`, `user`, `unknown`
- do not use row-level `source_type=synthetic` or `source_type=formula`
- do not use row-level `source_type=tool` just because a script wrote the workbook

## What To Read

- Read `references/workflow.md` before generating a workbook.
- Read `references/source-confidence-policy.md` before writing metadata.
- Read `references/verification.md` before final response.
- Use `track-sheet-sources` and `assess-sheet-confidence` after workbook creation; their product path is sidecar metadata.

## Data Source Priority

Use the best available source in this order:

1. user-uploaded files, existing workbook, database, or API result
2. public finance data through Akshare or another structured provider
3. opened web pages, annual reports, announcements, PDFs, or public reports
4. search results/snippets through Tavily/Serper when canonical pages are not opened
5. `llm` synthetic/demo data, clearly labeled in the workbook

For China public-company finance tasks, try Akshare first when available. Use Tavily/Serper to calibrate industry context and cite public sources. If the request explicitly says "simulate", "demo", or provides no real source data, synthetic data is allowed but must be visibly labeled.

## Required Output

Return a concise result:

- MaybeAI Sheet URL or local workbook path
- whether real data, public references, or synthetic/demo data were used
- sidecar metadata status: row count, source feature enabled, confidence feature enabled
- source distribution and confidence distribution
- any limitations or cells that remain low confidence

## Hard Prohibitions

- Do not create workbook-visible source/confidence audit worksheets unless the user explicitly asks for a standalone workbook-visible audit table.
- Do not write raw metadata into the workbook as the primary product path.
- Do not report success for source/confidence tracking until play-be sidecar upsert and verification pass.
- Do not accept a metadata result where all cells are `source_type=tool` and `confidence_level=2` unless the workbook truly has only one claim type and no recoverable upstream source. For generated finance workbooks this is almost always wrong.
