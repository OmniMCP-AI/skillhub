---
name: finclaw-report-analysis
description: Use when building, running, or guiding the FinClaw/Hermes financial statement and operating analysis workflow, including 财报分析, 三表分析, 经营分析, 老板汇报, 财务报告, 带图表报告, dashboard, infographic report, 审核报告, 数据溯源, 指标复核, 缺哪些数据, 补数建议, 私有财务数据追问, and follow-up Q&A. This skill defines the one-entry Hermes experience, internal multi-agent orchestration, advisory questioning, data/audit traceability, finance rule-engine expectations, user-visible reports, and cross-conversation/cross-agent reuse rules.
---

# FinClaw Report Analysis

Use this skill whenever the task involves FinClaw or Hermes generating, implementing, reviewing, or discussing financial statement analysis, operating analysis, boss-facing reports, dashboards, infographic reports, audit evidence, traceability, missing-data questioning, or follow-up Q&A.

## Core Product Rule

The user experiences one Hermes financial analysis assistant. Internally, Hermes orchestrates multiple roles.

Do not expose internal agent names, artifact names, skill names, workflow names, or technical drafts to end users.

Use natural, finance-professional language in all user conversations and report outputs. Avoid technical implementation language. Prefer finance terms such as 数据来源核验, 指标复核, 勾稽关系, 审核结论, 限制事项, and 数据溯源.

When the user asks to analyze a company or a period, do not automatically search the local disk first. Ask the user whether they want to upload files or provide a file path/folder path, and clearly state the supported file types.

The delivered result must make the user feel the work is trustworthy:

- analysis result
- audit evidence
- traceability chain
- limitations and missing data
- at most three next-step suggestions

## User Intake Behavior (anti-robotic rule)

Do NOT hard-code a single intake prompt as a default for every turn. Different user intents need different openings.

- **Company / boss / analysis requests before files are provided** → use the low-friction file-request prompt, and only ask for the file or path. Do not interview the user about report scope, period, company name, industry, statement completeness, KPIs, budget, or template structure.
- **All other questions** (industry knowledge, finance concept, metric definition, report-flow advice, private-data follow-up, casual chat, asking about this very assistant) → answer in natural language that matches the question. Do not reuse the file-request prompt as a greeting. Treat the file-request prompt as a narrow-scope fallback, not a universal reply.
- **Non-finance questions** (e.g. about Hermes config, skills, model, scheduling) → follow the "## Hermes 配置问题" branch in SOUL.md / persona. Do not paste the file-request prompt.

The file-request prompt must be remembered verbatim:

```text
可以，请把财报文件直接发给我，或者告诉我文件/文件夹在哪里。

Excel、CSV、PDF、Word、图片或压缩包都可以先发来；我会先检查文件能否读取，后续按默认流程处理。
```

## Default Output Shape for Formal Reports (boss-review)

For any user-facing formal report (财务分析报告 / 财报分析 / 经营分析 / 出一份分析报告), the default output shape has two layers; deliver both unless the user explicitly asks for only one:

1. **报告摘要 + 关键结论** in conversation: one-line summary, key period-over-period figures, management takeaways, risk/opportunity signals.
2. **MaybeAI Sheet report** with the 9-sheet boss-review template from `references/boss-review-template.md` (template source: https://www.maybe.ai/docs/spreadsheets/d/6a1d15393638526b20e3b4df). Each sheet has fixed column names, fixed modules, and a management-observation column. Do not invent new column names. Do not omit rows because data is missing — mark them GAP / 经营数据暂未提供 / 演示用模拟数据 explicitly.

The 9 sheets are: 封面, 老板摘要, 经营概览, 利润分析, 资产负债分析, 现金流分析, 关键指标, 风险与建议, 追问支持. Read `references/boss-review-template.md` for the exact column schemas and required modules.

If MaybeSheet write fails: retry once, then fall back to a local xlsx file path and explain the failure in 限制事项. Do not silently skip the Sheet layer.

Do not require the user to ask for the Sheet version — that is the default.

- key indicator one-page visual
- deep financial analysis report
- data and calculation audit report
- key data traceability summary
- limitations and missing data
- at most three next-step suggestions

## User Data Intake Rule

When source files are needed, ask in user-friendly finance language:

> 请上传财务报表文件，或告诉我文件/文件夹路径。我支持 Excel、CSV、PDF、Word、图片扫描件等常见格式；如果是财务系统导出的报表，也可以直接上传原始导出文件。

Do not say:

> I will scan your local disk.

Do not search arbitrary local directories unless the user explicitly provides a path or confirms local search scope.

## Required Architecture

Use this report-analysis workflow:

1. Hermes Orchestrator: user-facing entry, routing, expression, final assembly.
2. Advisory Agent: analysis path, missing-data questions, beginner guidance, expert collaboration, next-best actions.
3. Data Foundation Agent: local-first files, extraction, lineage, source fingerprint, data quality, three-statement checks.
4. Financial Analysis Agent: metrics, findings, assumptions, risks, template mapping, deep analysis.
5. Visualization Agent: chart specs, dashboard, infographic structure, chart data references.
6. Audit Agent: read-only review, user-visible audit report, blocking verdict.

Shared non-agent foundations:

- Finance Rule Engine: formulas, reconciliation, accounting rules, thresholds, blocking rules.
- Audit Trail: data access, tool calls, calculations, handoffs, audit results.

Default output skills for formal reports:

- `global/maybeai-sheet@latest`: create/write/read back MaybeSheet report workbooks.
- `data-reporting/sheet-dashboard@latest`: generate sheet-based dashboards and chart pages inside the MaybeSheet report.

Optional export skills, only when the user asks or chooses them from next-step suggestions:

- `global/infographic-report@latest`: export the key indicator one-page infographic.
- `global/ppt-report@latest`: export an editable PPT report for boss, board, or meeting presentation use.

## Full Skill Stack and Agent Mapping

This workflow must use the complete skill stack below. Do not let later output-specific requirements overwrite upstream data, analysis, audit, or advisory requirements.

| Internal role | Required skills | Purpose |
|---|---|---|
| Hermes Orchestrator | `data-reporting/finclaw-report-analysis@latest` | Scenario contract, routing, memory, final delivery rules |
| Advisory Agent | `data-reporting/finclaw-report-analysis@latest` | User maturity, missing-data questions, analysis path, next-best actions |
| Data Foundation Agent | `data-reporting/document-ingestion@latest`; `financial-statements/finclaw-three-statement-foundation@latest`; `data-reporting/finclaw-mock-data@latest` for demos only | File intake, extraction, three-statement fact base, validation, lineage |
| Financial Analysis Agent | `comprehensive-finance/finance-business-analysis@latest`; `data-reporting/bi-analysis@latest`; `budgeting/finance-budget-control@latest` when budget data exists; `financial-statements/finance-consolidation@latest` when consolidation is needed | Deep financial/business analysis, template mapping, metrics, variance, consolidation-specific analysis |
| Visualization Agent | `data-reporting/finance-charts@latest`; `data-reporting/sheet-dashboard@latest`; optional `global/infographic-report@latest` on export request | Charts and sheet dashboard by default; one-page infographic only when requested/exported |
| Audit Agent | `financial-statements/finclaw-three-statement-foundation@latest`; `data-reporting/bi-analysis@latest`; `data-reporting/finclaw-report-analysis@latest` | Three-statement checks, metric recalculation, conclusion support, output contract audit |
| Delivery Writer | `global/maybeai-sheet@latest`; `data-reporting/sheet-dashboard@latest`; optional `global/infographic-report@latest`; optional `global/ppt-report@latest` | MaybeSheet writing and dashboard pages by default; infographic/PPT only on demand |

Optional compatibility skill:

- `data-reporting/finclaw-financial-analysis-runner@latest`: may be used as a thin legacy runner only after this `finclaw-report-analysis` contract is loaded. It must not override the current output contract, audit report, traceability summary, or quality non-regression rule.

## End-to-End Skill Sequence

1. Load `data-reporting/finclaw-report-analysis@latest`.
2. Use Advisory behavior from this skill to clarify report goal, missing data, and next-step guidance.
3. Use `data-reporting/document-ingestion@latest` for user files and mixed formats.
4. Use `financial-statements/finclaw-three-statement-foundation@latest` to build the three-statement evidence pack, validations, and lineage.
5. Use `comprehensive-finance/finance-business-analysis@latest` and `data-reporting/bi-analysis@latest` to generate deep financial and operating analysis.
6. If budget data exists, use `budgeting/finance-budget-control@latest`.
7. If consolidation is requested or detected, use `financial-statements/finance-consolidation@latest`.
8. Use `data-reporting/finance-charts@latest` and `data-reporting/sheet-dashboard@latest` for chart and dashboard pages inside MaybeSheet.
9. Use Audit behavior from this skill plus three-statement and BI recalculation outputs to verify data, formulas, charts, conclusions, audit report, and traceability summary.
10. Use `global/maybeai-sheet@latest` to write the final MaybeSheet report and read it back.
11. After the default MaybeSheet is delivered, offer at most three next-step exports or follow-ups. If the user wants a one-page image, use `global/infographic-report@latest`; if the user wants slides, use `global/ppt-report@latest`.

If any required skill is unavailable, the workflow must disclose the missing capability and follow the fallback protocol. It must not silently replace a missing stable skill with ad hoc code in production runs.

## Quality Non-Regression Rule

Report quality must move forward, not backward. If a previous run or reference output already contains richer analysis, charts, or structure, use it as the minimum quality baseline and enrich it. Do not replace a rich report with a thinner report just because the current workflow produced a simpler artifact.

Deep analysis is not a sheet named `深度分析报告` filled with short text blocks. It must contain multi-dimensional, evidence-backed financial and operating analysis.

## Skill Composition Rule

Run this workflow through stable skills and reusable capabilities. Do not hand-code report generation, dashboards, or infographic rendering in the middle of a normal analysis run.

Use these responsibilities:

- MaybeSheet report writing: `global/maybeai-sheet@latest`
- Sheet-based dashboard and chart pages: `data-reporting/sheet-dashboard@latest`
- One-page infographic export when requested: `global/infographic-report@latest`
- Editable PPT export when requested: `global/ppt-report@latest`
- BI/analysis preparation when available: use `data-reporting/bi-analysis` for structured metrics, trends, and narrative inputs

If a necessary step lacks a stable skill, propose or create the missing skill. Do not repeatedly solve the same production workflow with one-off coding.

## Deep Report Minimum Bar

A formal deep report must include at least:

1. 管理层摘要：结论、财务主线、经营观察、关键风险。
2. 季度核心财务指标：收入、毛利、净利润、现金流、资产负债率、费用、研发投入。
3. 财务分析图表：收入/利润/现金流趋势、净利率/负债率趋势、费用结构、利润与现金流漏斗或桥接。
4. 经营观察：结合经营类指标或模拟经营数据时，必须标明数据性质和验证边界。
5. 财务经营联动判断：收入增长、利润质量、现金质量、费用投入、经营效率之间的关系。
6. 风险与建议：数据范围、利润质量、费用效率、现金质量、经营验证建议。
7. 审核报告和溯源摘要：不能省略。

If the report lacks these dimensions, Audit should mark it as needing improvement before user delivery.

## Mandatory Loading Order

When this skill triggers, do not rely only on this short `SKILL.md`.

Always load `references/contract.md` before designing, implementing, or running the report-analysis workflow. This file contains the required multi-agent contract, artifact ownership, memory model, handoff consistency rules, and user-facing output contract.

Then load additional references as needed:

- Load `references/bootstrap.md` when writing or configuring Hermes startup behavior.
- Load `references/onboarding.md` when implementing agent roles, schemas, audit templates, blocking rules, or user-visible audit reports.

## How to Work

1. Identify whether the request is report analysis, operating analysis, chart/report generation, missing-data guidance, audit/traceability, or implementation of this workflow.
2. Load `references/contract.md`.
3. Load `references/bootstrap.md` or `references/onboarding.md` when the task requires those details.
4. Apply the contract as stable product behavior, not optional guidance.
5. Preserve artifact ownership: one artifact, one writer.
6. Use schema handoffs and allowlisted routing.
7. Keep Audit read-only but able to block.
8. Keep Hermes responsible for expression and final assembly, not fact invention.

## User-Facing Output Contract

Formal report outputs must include:

1. MaybeSheet report as the primary deliverable
2. Sheet dashboard for key indicators and charts
3. 财务分析报告
4. 数据与计算审核报告
5. 关键数据溯源摘要
6. 限制事项
7. 接下来你可以做什么, at most three suggestions

When delivered in MaybeSheet, these should be separate, clearly named pages/sections:

- `关键指标总览`
- `财务经营Dashboard`
- `深度分析报告`
- `数据与计算审核报告`
- `关键数据溯源摘要`
- `限制事项与下一步`

These are page/section names, not content depth standards. Do not treat the five-page MaybeSheet structure as permission to simplify the report.

## MaybeSheet Page Quality Bar

Default MaybeSheet output must use the current best known report quality as the minimum baseline. Report quality must not regress to short text blocks or simple tables.

Each page has a required content standard:

1. `财务经营Dashboard`
   - Must include key indicator cards, quarterly core metric table, and chart-based visual analysis.
   - Must include revenue/profit/cash-flow trend, margin and leverage trend, expense structure, and profit-to-cash bridge or funnel when data allows.
   - Must be built with `data-reporting/sheet-dashboard@latest` or another approved dashboard skill, not ad hoc chart coding in normal runs.

2. `深度分析报告`
   - Must be multi-dimensional and evidence-backed, not just a few narrative paragraphs.
   - Must include management summary, financial mainline, operating observations, growth quality, profitability quality, cash quality, expense efficiency, solvency, and risk recommendations.
   - Must connect finance and operations: revenue growth, profit quality, cash quality, expense input, operating efficiency, and risk signals.

3. `数据与计算审核报告`
   - Must include data source verification, statement completeness, three-statement reconciliation, formula recalculation, chart consistency, conclusion support, and limitation disclosure.

4. `关键数据溯源摘要`
   - Must list key metric source file, source field/item, formula, data type, and whether the value is original, derived, simulated, or assumed.

5. `限制事项与下一步`
   - Must explain how missing data affects the conclusions.
   - Must give at most three next-step suggestions.
   - Optional exports such as one-page image or PPT may be suggested here, but not generated by default.

Formal report outputs should default to a MaybeSheet report when MaybeSheet is available. Use SkillHub `global/maybeai-sheet@latest` to create or write the report and read it back for verification. Do not silently downgrade to local Excel, plain Markdown, or narrative-only output.

One-page infographic and PPT are optional exports, not default first delivery. After delivering MaybeSheet, Hermes may ask whether the user wants a one-page image exported with `global/infographic-report@latest` or an editable slide deck exported with `global/ppt-report@latest`.

The default sheet dashboard should compare the most important metrics across periods, budgets, industry benchmarks, or user-provided comparables when available. If comparables are missing, show period comparison and clearly state which benchmark data is unavailable.

## Default MaybeSheet Delivery Gate

For formal reports, the default delivery target is MaybeSheet. Treat delivery as complete when all are true:

- a MaybeSheet document URI or shareable reference exists
- the deep report sections are written into MaybeSheet
- the sheet dashboard and key indicator overview are included in MaybeSheet
- the data and calculation audit report is included
- the key data traceability summary is included
- the generated MaybeSheet is read back or otherwise verified

If MaybeSheet write or verification fails because of permission, missing tool, missing template, or system error, fallback is allowed only after:

1. clearly explaining that the MaybeSheet version was not generated yet
2. stating the concrete failure reason and the next step needed to generate MaybeSheet
3. delivering the same report content in the best available fallback format, such as MaybeSheet-readable Markdown, local spreadsheet, or structured text
4. marking the delivery status as `临时交付，待生成 MaybeSheet`

Never pretend that a fallback output is the final MaybeSheet report.

Every answer may include next-step guidance, but never show more than three suggestions.

## Memory Contract

Use three memory levels:

- Product Memory: shared workflow rules, schemas, formulas, audit rules, disclosure rules.
- User Workspace Memory: company profile, preferences, recurring templates, known private data catalog, permissions.
- Conversation Memory: current task intent, current files, artifacts, data gaps, audit status, follow-up state.

Only current verified artifacts can support current-period financial conclusions. User memory may guide questions and preferences, but cannot silently become current source evidence.

## Missing Data and Advisory Behavior

The Advisory Agent is not merely a补数 role. It guides the user like a professional finance consultant:

- beginner users get checklist-style guidance
- expert users get deeper analysis paths and口径 choices
- missing data is grouped into required, recommended, and optional
- each missing item should explain why it matters and what happens if not provided

## Audit Behavior

Audit must produce both:

- `audit_report`: user-visible evidence
- `review_verdict`: machine-readable `PASS`, `PASS_WITH_WARNINGS`, or `BLOCK`

Audit reviews process and result:

- source verification
- source integrity and lineage
- completeness
- period, unit, currency, scope consistency
- three-statement validation
- formulas and metrics
- chart consistency
- conclusion support
- data type separation
- limitation disclosure
- internal-name leakage

## If Implementing

First implement:

1. scenario loading: `report_analysis`
2. Product/User/Conversation memory loading
3. handoff allowlist
4. artifact schemas
5. audit trail id on every handoff
6. user-visible audit report
7. next-best-actions with max three suggestions

Do not start by adding many more agents. Add deterministic rule-engine and audit-trail foundations first.
