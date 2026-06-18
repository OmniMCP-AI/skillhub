---
name: traceable-financial-analysis
description: Guides the Hermes financial statement and operating analysis workflow, including 财报分析, 三表分析, 经营分析, 老板汇报, 审核报告, 数据溯源, 指标复核, 缺哪些数据, and follow-up Q&A. Use when the task needs a finance-professional business contract, boss-review report structure, audit visibility, metric consistency, traceability, or missing-data guidance.
version: 0.1.0
---

# Traceable Financial Analysis

This skill is the business and product contract for the financial-analysis workflow.

It owns:

- what the user-facing finance product should feel like
- what a complete report must contain
- what metrics, narratives, risks, and audit outputs mean
- how formal financial analysis work should be structured and reviewed

It does not own low-level MaybeAI Sheet mechanics.

## Use when

Trigger this skill for:

- 财报分析 / 三表分析 / 经营分析
- 老板汇报 / 财务报告 / dashboard / infographic report
- 审核报告 / 数据溯源 / 指标复核
- follow-up Q&A on an existing FinClaw report
- implementation or review of the FinClaw workflow itself

## Core product rules

1. The user experiences one Hermes financial analysis assistant.
2. User-facing language must stay finance-professional, not implementation-heavy.
3. The deliverable must include analysis, audit evidence, traceability, limitations, and at most three next-step suggestions.
4. Formal reports must separate raw facts, normalized metrics, and output rendering.
5. Audit may block delivery when consistency or support is insufficient.

## User intake rule

Do not automatically search arbitrary local disk locations before the user gives a path or confirms scope.

When files are needed, use this prompt:

```text
可以，请把财报文件直接发给我，或者告诉我文件/文件夹在哪里。

Excel、CSV、PDF、Word、图片或压缩包都可以先发来；我会先检查文件能否读取，后续按默认流程处理。
```

## Default formal output

For a formal boss-facing report, default to two layers unless the user explicitly narrows scope:

1. conversation summary with key conclusions
2. MaybeAI Sheet report using the 9-sheet boss-review structure

The 9 sheets are:

- 封面
- 老板摘要
- 经营概览
- 利润分析
- 资产负债分析
- 现金流分析
- 关键指标
- 风险与建议
- 追问支持

Read `references/boss-review-template.md` for the exact sheet contract.

## Skill boundaries

- `traceable-financial-analysis`: business contract, finance meaning, report structure, audit expectations
- `maybeai-formula-report`: traceable raw + formula workbook orchestration
- `maybeai-sheet`: underlying MaybeAI Sheet API operations

Do not store backend-specific worksheet quirks or formula activation sequences here unless they directly change the business contract.

## Mandatory loading order

When this skill triggers:

1. Always read `references/contract.md`.
2. For formal report generation, read `references/boss-review-template.md`.
3. If the workbook uses normalized three-statement sheets as formula sources, read `references/statement-sheet-mapping.md`.
4. Read `references/onboarding.md` when implementing roles, schemas, audit artifacts, or handoff behavior.
5. Read `references/bootstrap.md` only when changing startup or initialization behavior.

## Workflow summary

1. Clarify report goal and source scope.
2. Build or validate the three-statement evidence base.
3. Normalize metrics with explicit grain and unit.
4. Generate findings, risks, and management takeaways from approved evidence.
5. Render the report using the fixed business contract.
6. Run audit and traceability checks before delivery.

## Quality gates

Block or revise the report if any of these fail:

- dashboard, narrative, and audit cite inconsistent numbers
- metric grain is ambiguous or mislabeled
- units are mixed inside one derived metric
- conclusions are not supported by evidence
- limitations or missing data are hidden

## Reference map

- `references/contract.md`
  Full multi-agent contract, artifact ownership, metric consistency, audit authority, and anti-drift rules.
- `references/boss-review-template.md`
  Exact 9-sheet boss-review structure and required modules.
- `references/statement-sheet-mapping.md`
  Three-statement normalized worksheet layout and row mapping for formula-driven report builds.
- `references/onboarding.md`
  Agent responsibilities, schemas, artifact ownership, and audit behavior.
- `references/bootstrap.md`
  Startup and initialization behavior.

## Composition rules

- Use `maybeai-formula-report` when the workbook must preserve formula lineage from raw tabs to report tabs.
- Use `maybeai-sheet` for sheet creation, reads, writes, and verification.
- Use `sheet-dashboard` for dashboard and chart pages.
- Do not hand-code one-off report pipelines when an existing skill already owns the workflow.

## Minimum delivery bar

A formal report must include:

- management summary
- core financial trend analysis
- chart or dashboard support when requested or defaulted by the workflow
- risk and recommendation coverage
- visible audit result
- visible traceability or source explanation

If these are missing, the report is incomplete.
