# FinClaw Hermes Multi-Agent Onboarding

## 1. Goal

FinClaw is a finance-facing analysis system. The user should be able to ask in one sentence and receive a reviewable, traceable, chart-ready financial analysis report.

The user should not see internal skill names, workflow names, scratch files, or technical drafts. The user should see:

1. A deep financial analysis report.
2. A visible data and calculation audit report.
3. A source traceability summary for key numbers and conclusions.

The key product promise is:

> FinClaw does not only provide an answer. It provides the answer, the review evidence, and the traceability chain.

## 2. Design Principles

### 2.1 Workflow Agents, Not Fragmented Tool Agents

Agents are organized by workflow responsibility, not by tiny capabilities.

Use a small number of strong workflow agents:

- Orchestrator Agent
- Advisory Agent
- Data Foundation Agent
- Financial Analysis Agent
- Visualization Agent
- Audit Agent

Do not create separate user-facing agents for every ability such as "ratio calculator", "chart picker", "template mapper", or "Kingdee connector" unless the workflow becomes large enough to justify it.

### 2.2 No Free Agent-to-Agent Chat

Sub-agents must not talk to each other directly.

All handoffs go through the Orchestrator Agent and must use:

- allowlist
- task id
- input schema
- output artifact schema
- artifact owner

### 2.3 One Artifact, One Writer

Each artifact has exactly one writer. Other agents may read, review, or comment, but must not overwrite it.

| Artifact | Writer | Purpose |
|---|---|---|
| `financial_evidence_pack` | Data Foundation Agent | Source files, extracted statements, data lineage, validation results |
| `data_quality_report` | Data Foundation Agent | Missing fields, inconsistent units, suspicious values, quality warnings |
| `analysis_pack` | Financial Analysis Agent | Metrics, financial findings, hypotheses, risk flags, template mapping |
| `visualization_pack` | Visualization Agent | Chart specs, dashboard sections, infographic outline, chart data references |
| `audit_report` | Audit Agent | User-visible evidence that data, formulas, charts, and conclusions were reviewed |
| `review_verdict` | Audit Agent | `PASS`, `PASS_WITH_WARNINGS`, or `BLOCK` |
| `final_report` | Orchestrator Agent | User-facing report assembled from approved artifacts |

### 2.4 The Auditor Is Read-Only But Can Block

The Audit Agent must not modify data, analysis, charts, or final report content directly.

It may return:

- `PASS`: continue.
- `PASS_WITH_WARNINGS`: continue, but warnings and limitations must be shown to the user.
- `BLOCK`: stop and return the artifact to the responsible owner for rework.

If the issue cannot be fixed from available data, the Orchestrator Agent asks the user for the missing file, field, or clarification.

### 2.5 Orchestrator Owns Expression, Not Facts

The Orchestrator Agent may:

- understand user intent
- choose the workflow
- call agents
- maintain conversation state
- assemble the final user-facing answer
- control language, tone, structure, and disclosure

The Orchestrator Agent must not:

- alter original data
- invent financial facts
- recalculate metrics differently from the evidence pack or analysis pack
- remove audit limitations
- turn assumptions into verified facts

Short rule:

> The Orchestrator Agent expresses and assembles. It does not invent facts.

## 3. Agent Roles

### 3.1 Orchestrator Agent

User-facing owner. The user should feel they are interacting with one financial analysis assistant.

Responsibilities:

- Parse user intent.
- Detect language. Chinese input defaults to Chinese output.
- Decide workflow: analysis only, analysis plus charts, dashboard, infographic report, follow-up Q&A, template-based report.
- Prefer local financial files first. If unavailable, ask the user to upload. Future Kingdee integration is a data source under Data Foundation Agent.
- Manage period, company, currency, unit, consolidation scope, and report type.
- Dispatch handoffs through allowlisted tasks.
- Assemble final report from reviewed artifacts.
- Surface audit report and traceability summary to the user.

Must not:

- expose internal agent names or skill names to end users
- create unsupported conclusions
- hide audit warnings

### 3.2 Advisory Agent

Owner of professional finance conversation guidance.

Responsibilities:

- Detect user maturity: beginner, intermediate, expert, or unknown.
- Design analysis path and question strategy.
- Group missing data into required, recommended, and optional.
- Explain why each missing item matters and what happens if it is not provided.
- Provide beginner checklist mode and expert collaboration mode.
- Generate at most three next-best actions after each answer.

Must not:

- extract source data
- calculate metrics
- write final reports
- replace the audit function

### 3.3 Data Foundation Agent

Owner of facts and source evidence.

Responsibilities:

- Search local files first.
- Identify financial statements.
- Extract balance sheet, income statement, and cash flow statement.
- Identify period, company, currency, unit, consolidation scope.
- Preserve source lineage: file name, sheet name, row/column/cell range when available.
- Record source file fingerprint or stable file metadata when available.
- Validate three-statement foundation:
  - balance sheet balance
  - period consistency
  - unit and currency consistency
  - cash flow reconciliation where data allows
- Distinguish data types:
  - financial statement data
  - operational data
  - user-provided data
  - simulated data
  - derived metrics
  - assumptions
- Produce `financial_evidence_pack` and `data_quality_report`.

Must not:

- write final analysis conclusions
- silently mix actual and simulated data
- overwrite original source files

### 3.4 Financial Analysis Agent

Owner of financial insights.

Responsibilities:

- Consume only approved evidence from `financial_evidence_pack`.
- Map default templates and user-defined templates.
- Calculate and explain metrics:
  - revenue growth
  - gross margin
  - net margin
  - expense ratios
  - asset-liability ratio
  - current ratio
  - operating cash flow to net profit
  - receivables turnover
  - inventory turnover
  - other template-required metrics
- Produce deep analysis:
  - profitability
  - growth
  - cash flow quality
  - solvency
  - operating efficiency
  - expense structure
  - risk signals
  - possible business explanations
- Clearly mark assumptions and unsupported hypotheses.
- Produce `analysis_pack`.

Must not:

- modify source data
- treat business hypotheses as verified operational facts
- create chart data directly

### 3.5 Visualization Agent

Owner of chart and presentation artifacts.

Responsibilities:

- Consume `financial_evidence_pack` and `analysis_pack`.
- Decide chart types that support the analysis:
  - trend charts
  - comparison charts
  - waterfall charts
  - structure charts
  - ratio dashboards
  - risk indicator panels
- Generate chart specs and data references.
- Generate dashboard section structure.
- Generate infographic outline when requested.
- Ensure chart data points trace back to approved source fields or reviewed metrics.
- Produce `visualization_pack`.

Must not:

- invent new financial conclusions
- change metric formulas
- use unaudited data

### 3.6 Audit Agent

Independent read-only reviewer.

Responsibilities:

- Review source data, extraction, formulas, analysis conclusions, charts, and final draft.
- Produce user-visible `audit_report`.
- Produce machine-readable `review_verdict`.
- Block delivery if critical issues exist.

Audit dimensions:

1. Data source verification
2. File integrity and source lineage
3. Statement completeness
4. Period, unit, currency, and scope consistency
5. Three-statement validation
6. Data quality checks
7. Formula and metric recalculation
8. Statistical aggregation checks
9. Chart data consistency
10. Conclusion support check
11. Separation of financial, operational, simulated, derived, and assumed data
12. Limitation and disclosure check
13. User-facing language check
14. Internal-name leakage check

Must not:

- edit business artifacts
- create substitute analysis
- remove limitations

## 4. Handoff Allowlist

## 3.7 Full Skill Stack and Agent Mapping

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

- `data-reporting/finclaw-financial-analysis-runner@latest`: may be used as a thin legacy runner only after the current `finclaw-report-analysis` contract is loaded.

Do not let output-only skills override upstream data, analysis, audit, or advisory requirements.

| From | To | Allowed Tasks |
|---|---|---|
| Orchestrator | Data Foundation | `build_financial_evidence_pack`, `repair_financial_evidence_pack` |
| Orchestrator | Financial Analysis | `build_analysis_pack`, `repair_analysis_pack` |
| Orchestrator | Visualization | `build_visualization_pack`, `repair_visualization_pack` |
| Orchestrator | Audit | `review_artifacts`, `review_final_report` |
| Data Foundation | Orchestrator | return `financial_evidence_pack`, `data_quality_report` |
| Financial Analysis | Orchestrator | return `analysis_pack` |
| Visualization | Orchestrator | return `visualization_pack` |
| Audit | Orchestrator | return `audit_report`, `review_verdict` |

Not allowed:

- Data Foundation directly calls Financial Analysis.
- Financial Analysis directly calls Visualization.
- Visualization directly calls Audit.
- Audit directly modifies any artifact.

## 5. Core Schemas

### 5.1 Handoff Request

```json
{
  "handoff_id": "string",
  "from_agent": "orchestrator",
  "to_agent": "data_foundation | financial_analysis | visualization | audit",
  "task": "string",
  "user_intent": "string",
  "language": "zh-CN",
  "company": "string|null",
  "period": "string|null",
  "constraints": {
    "source_priority": ["local_files", "user_upload", "kingdee"],
    "output_format": "report | dashboard | infographic | qa",
    "template": "default | user_defined"
  },
  "input_artifacts": [],
  "expected_output_artifacts": []
}
```

### 5.2 Financial Evidence Pack

```json
{
  "artifact": "financial_evidence_pack",
  "owner": "data_foundation",
  "company": null,
  "periods": [],
  "currency": null,
  "unit": null,
  "scope": null,
  "source_files": [
    {
      "file_name": "string",
      "file_path_or_uri": "string",
      "fingerprint": "string|null",
      "detected_type": "balance_sheet | income_statement | cash_flow_statement | mixed | unknown",
      "sheets": []
    }
  ],
  "statements": {
    "balance_sheet": {},
    "income_statement": {},
    "cash_flow_statement": {}
  },
  "lineage": [
    {
      "field": "string",
      "value": "number|string|null",
      "data_type": "financial_statement | operational | user_provided | simulated | derived_metric | assumption",
      "source_file": "string|null",
      "source_sheet": "string|null",
      "source_range": "string|null"
    }
  ],
  "validations": {
    "statement_completeness": "pass | warning | fail",
    "period_consistency": "pass | warning | fail",
    "unit_consistency": "pass | warning | fail",
    "currency_consistency": "pass | warning | fail",
    "balance_sheet_equation": "pass | warning | fail | not_applicable",
    "cash_flow_reconciliation": "pass | warning | fail | not_applicable"
  },
  "quality_issues": [],
  "missing_items": [],
  "confidence": "high | medium | low"
}
```

### 5.3 Analysis Pack

```json
{
  "artifact": "analysis_pack",
  "owner": "financial_analysis",
  "template": {
    "type": "default | user_defined",
    "coverage": "high | medium | low",
    "unmapped_sections": []
  },
  "metrics": [
    {
      "name": "string",
      "value": "number|string|null",
      "formula": "string",
      "inputs": [],
      "data_type": "derived_metric",
      "confidence": "high | medium | low"
    }
  ],
  "findings": [
    {
      "title": "string",
      "claim": "string",
      "supporting_metrics": [],
      "source_fields": [],
      "confidence": "high | medium | low"
    }
  ],
  "risks": [],
  "assumptions": [],
  "unsupported_questions": []
}
```

### 5.4 Visualization Pack

```json
{
  "artifact": "visualization_pack",
  "owner": "visualization",
  "charts": [
    {
      "chart_id": "string",
      "title": "string",
      "chart_type": "bar | line | combo | waterfall | pie | table | heatmap | KPI",
      "purpose": "string",
      "data_refs": [],
      "supports_findings": [],
      "warnings": []
    }
  ],
  "dashboard_sections": [],
  "infographic_outline": [],
  "confidence": "high | medium | low"
}
```

### 5.5 Audit Report

```json
{
  "artifact": "audit_report",
  "owner": "audit",
  "overall_result": "pass | pass_with_warnings | block",
  "overall_confidence": "high | medium | low",
  "checks": [
    {
      "dimension": "data_source | integrity | completeness | reconciliation | formula | chart_consistency | conclusion_support | disclosure | leakage",
      "result": "pass | warning | fail | not_applicable",
      "summary": "string",
      "evidence_refs": [],
      "required_action": "string|null"
    }
  ],
  "limitations": [],
  "blocking_issues": [],
  "user_visible_summary": "string"
}
```

### 5.6 Review Verdict

```json
{
  "artifact": "review_verdict",
  "owner": "audit",
  "status": "PASS | PASS_WITH_WARNINGS | BLOCK",
  "blocked_artifact": "financial_evidence_pack | analysis_pack | visualization_pack | final_report | null",
  "return_to_agent": "data_foundation | financial_analysis | visualization | orchestrator | null",
  "required_fixes": [],
  "warnings_to_disclose": []
}
```

## 6. Default Workflow

### 6.1 Full Financial Analysis With Charts

1. User asks a question.
2. Orchestrator parses intent, language, period, company, output type.
3. Orchestrator asks Data Foundation to build `financial_evidence_pack`.
4. If no local data is found, Orchestrator asks the user to upload files.
5. Data Foundation extracts statements, records lineage, validates data, and returns evidence artifacts.
6. Orchestrator sends evidence to Audit for data-stage review when:
   - three statements are found
   - source files are complex
   - user asks whether data is accurate
   - the output is formal or boss-facing
7. Orchestrator asks Financial Analysis to build `analysis_pack`.
8. Orchestrator asks Visualization to build `visualization_pack` if charts are required.
9. Orchestrator asks Audit to review evidence, analysis, and visualization artifacts.
10. If Audit returns `BLOCK`, Orchestrator routes rework to the artifact owner.
11. If Audit returns `PASS` or `PASS_WITH_WARNINGS`, Orchestrator assembles:
    - financial analysis report
    - data and calculation audit report
    - source traceability summary
12. Orchestrator asks Audit to review the final user-facing report.
13. Orchestrator returns final output to the user.

## 7. User-Visible Output Contract

The final response must include:

1. `MaybeSheet报告`
2. `财务经营Dashboard`
3. `财务分析报告`
4. `数据与计算审核报告`
5. `关键数据溯源摘要`
6. `限制事项`
7. `可追问方向`

When delivered in MaybeSheet, use separate, clearly named pages/sections:

- `关键指标总览`
- `财务经营Dashboard`
- `深度分析报告`
- `数据与计算审核报告`
- `关键数据溯源摘要`
- `限制事项与下一步`

These are page/section names, not content depth standards. Do not treat the five-page MaybeSheet structure as permission to simplify the report.

Each page has a required content standard:

1. `财务经营Dashboard`: key indicator cards, quarterly core metric table, and chart-based visual analysis; revenue/profit/cash-flow trend, margin and leverage trend, expense structure, and profit-to-cash bridge or funnel when data allows.
2. `深度分析报告`: management summary, financial mainline, operating observations, growth quality, profitability quality, cash quality, expense efficiency, solvency, and risk recommendations.
3. `数据与计算审核报告`: data source verification, statement completeness, three-statement reconciliation, formula recalculation, chart consistency, conclusion support, and limitation disclosure.
4. `关键数据溯源摘要`: key metric source file, source field/item, formula, data type, and whether the value is original, derived, simulated, or assumed.
5. `限制事项与下一步`: missing-data impact and at most three next-step suggestions; optional exports may be suggested but not generated by default.

When MaybeSheet is available, formal reports should default to a MaybeSheet report using SkillHub `global/maybeai-sheet@latest`, not a local Excel file, plain Markdown answer, or narrative-only response.

Default MaybeSheet delivery is complete when:

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

One-page infographic and PPT are optional exports, not default first delivery. After delivering MaybeSheet, Hermes may ask whether the user wants a one-page image exported with `global/infographic-report@latest` or an editable slide deck exported with `global/ppt-report@latest`.

The default sheet dashboard should be scannable and attention-grabbing for executives. It should include:

- key indicators such as revenue, gross margin, net profit, operating cash flow, asset-liability ratio, receivables turnover, inventory turnover, and other user-relevant metrics
- comparison across periods when available
- budget/target comparison when available
- industry or peer comparison when available
- key status labels such as 改善, 承压, 异常, 待补充
- short finance-language interpretation for each major signal

Inputs to dashboard/export skills should come from reviewed evidence, reviewed analysis, and reviewed visualization data. They must not add new financial conclusions or unaudited numbers.

If budget, target, industry, or peer data is unavailable, do not invent it. Use period comparison and disclose the missing benchmark data.

The final response must not include:

- internal agent names
- skill names
- workflow file names
- scratch artifact names such as `analysis_pack`
- unsupported certainty

The final response must not regress from known richer outputs. A formal deep report must include management summary, quarterly financial indicators, financial charts, operating observations, finance-operating linkage judgments, risks and recommendations, audit report, and traceability summary. A sheet named `深度分析报告` with short narrative blocks is not sufficient.

It may say:

> 本报告已完成数据来源核验、三表完整性核验、指标计算复核、图表一致性复核和结论支撑性检查。

It should not say:

> Data Foundation Agent produced financial_evidence_pack and Audit Agent returned PASS.

## 8. User-Visible Audit Report Template

```markdown
## 数据与计算审核报告

### 审核结论
综合审核结果：通过 / 有限制通过 / 暂不通过
可信度：高 / 中 / 低

### 1. 数据来源核验
- 使用文件：
- 报表期间：
- 币种/单位：
- 数据类型：
- 源文件指纹：

### 2. 报表完整性核验
- 资产负债表：
- 利润表：
- 现金流量表：
- 期间一致性：
- 单位一致性：

### 3. 三表勾稽核验
- 资产 = 负债 + 所有者权益：
- 现金及现金等价物净增加额：
- 净利润与经营现金流方向性：

### 4. 指标计算复核
已复核关键指标公式：
- 毛利率 = 毛利 / 营业收入
- 净利率 = 净利润 / 营业收入
- 资产负债率 = 总负债 / 总资产
- 经营现金流净额 / 净利润
- 应收账款周转率
- 存货周转率

复核结果：

### 5. 图表一致性复核
- 图表数据来源：
- 图表与正文结论一致性：

### 6. 结论支撑性检查
- 核心结论是否可追溯：
- 是否存在无数据支撑的确定性表述：

### 7. 数据类型区分
- 财务数据：
- 经营数据：
- 模拟数据：
- 推导指标：
- 分析假设：

### 8. 限制事项
- 缺失数据：
- 不可验证事项：
- 仅作为假设的经营解释：
```

## 9. Blocking Rules

Audit must return `BLOCK` when:

- source data is missing for a core conclusion
- three statements are incomplete but the report claims full financial analysis
- balance sheet equation fails without explanation
- unit or currency is mixed and not normalized
- formulas produce inconsistent results
- charts use unaudited or unsupported data
- simulated data is presented as actual data
- operational assumptions are presented as verified facts
- final report hides important limitations
- internal agent or skill names leak to the user
- formal report defaulted to MaybeSheet, MaybeSheet failed, and the fallback protocol was not followed
- fallback output is presented as the final MaybeSheet report
- formal deep report lacks multi-dimensional analysis, financial charts, finance-operating linkage, audit report, or traceability summary
- production workflow hand-codes dashboard/infographic/report rendering instead of using the required stable skills without an explicit prototyping reason

Audit may return `PASS_WITH_WARNINGS` when:

- data is sufficient for the requested report but some optional dimensions are missing
- business attribution cannot be verified from financial statements alone
- period comparison is limited
- only partial charts can be generated
- source files are usable but have minor formatting issues

## 10. First Implementation Scope

Implement in this order:

1. Handoff allowlist and schemas.
2. Data Foundation output with lineage and validations.
3. Audit Agent output with `audit_report` and `review_verdict`.
4. Orchestrator final output contract.
5. Financial Analysis pack.
6. Visualization pack.
7. Final-report audit pass.
8. Follow-up Q&A using the same artifacts.

Do not start by building many agents. Start by making artifacts and audit evidence reliable.

## 11. Example End-to-End User Output Shape

```markdown
# 2025年度财务分析报告

## 财务经营Dashboard

| 指标 | 本期 | 上期/同期 | 变化 | 状态 | 一句话解读 |
|---|---:|---:|---:|---|---|
| 营业收入 | ... | ... | ... | 改善/承压/异常 | ... |
| 毛利率 | ... | ... | ... | 改善/承压/异常 | ... |
| 净利润 | ... | ... | ... | 改善/承压/异常 | ... |
| 经营现金流净额 | ... | ... | ... | 改善/承压/异常 | ... |
| 资产负债率 | ... | ... | ... | 改善/承压/异常 | ... |

## 核心结论
...

## 深度分析
...

## 图表
...

## 数据与计算审核报告

本报告已完成数据来源核验、三表完整性核验、指标计算复核、图表一致性复核和结论支撑性检查。

综合审核结果：通过
可信度：高

### 已完成复核
- 数据来源核验：通过
- 报表完整性核验：通过
- 三表勾稽核验：通过
- 指标计算复核：通过
- 图表一致性复核：通过
- 结论支撑性检查：通过

### 限制事项
未提供分产品、分客户、分区域经营数据，因此相关经营归因仅作为分析假设，不作为已验证事实。

## 关键数据溯源摘要

| 指标 | 数值 | 来源 | 计算方式 |
|---|---:|---|---|
| 营业收入 | ... | 利润表 | 原始报表项目 |
| 净利率 | ... | 利润表 | 净利润 / 营业收入 |
```
