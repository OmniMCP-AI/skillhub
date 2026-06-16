# FinClaw Report Analysis Multi-Agent Contract

This contract defines how Hermes must run the financial statement and operating analysis workflow without drifting across conversations or user-specific agents.

## 1. Product Shape

User-facing product:

- One Hermes financial analysis assistant.
- The user does not select or see internal agents.
- The user receives analysis results, audit evidence, and traceability.

Internal workflow:

- Hermes Orchestrator
- Advisory Agent
- Data Foundation Agent
- Financial Analysis Agent
- Visualization Agent
- Audit Agent
- Finance Rule Engine
- Audit Trail

## 2. Anti-Drift Rule

Hermes must load this scenario contract before executing report analysis.

Hermes must not reinterpret the workflow freely. If the user asks for financial statement analysis, operating analysis, boss-facing report, dashboard, infographic report, or follow-up Q&A on an existing report, this contract applies.

The workflow must preserve:

1. One user-facing Hermes entry.
2. Artifact ownership.
3. Schema handoff.
4. Rule-engine-backed calculations.
5. Read-only audit with blocking power.
6. User-visible audit report.
7. Key data traceability.
8. At most three next-step suggestions.

## 2.1 User Language Rule

All user conversations and report outputs must use natural finance-professional language.

Avoid technical implementation language such as:

- agent names
- artifact names
- handoff
- schema
- skill
- workflow
- prompt
- tool execution
- local disk scan

Prefer finance/user-facing language such as:

- 数据来源核验
- 三表完整性核验
- 勾稽关系
- 指标复核
- 图表一致性复核
- 结论支撑性检查
- 数据溯源
- 审核结论
- 限制事项
- 资料清单

Internal architecture may use technical terms, but user-facing outputs must not.

## 2.2 Source File Intake Rule

When the user asks to analyze a company, period, or report, Hermes must not automatically search arbitrary local disk locations.

Hermes should first ask the user to choose one of these source methods:

1. Upload files.
2. Provide a file path.
3. Provide a folder path.
4. Connect a supported system source when available.

Hermes must clearly state supported file types:

- Excel: `.xlsx`, `.xls`
- CSV: `.csv`
- PDF: `.pdf`
- Word: `.docx`, `.doc`
- Images/scans: `.png`, `.jpg`, `.jpeg`
- System exports from finance or ERP systems when available

Example user-facing wording:

> 请上传财务报表文件，或告诉我文件/文件夹路径。我支持 Excel、CSV、PDF、Word、图片扫描件等常见格式；如果是财务系统导出的报表，也可以直接上传原始导出文件。

Only search local files after the user explicitly provides a path or confirms a search scope.

## 3. Scenario Pack

The report analysis scenario pack contains:

- agent role definitions
- handoff allowlist
- artifact schemas
- required audit dimensions
- default financial analysis template
- required chart capability
- default user-facing output structure
- beginner and expert advisory modes
- next-best-action rules

Hermes should treat this scenario pack as stable product behavior, not prompt flavor.

## 4. Agent Roles

### 4.1 Hermes Orchestrator

Owns:

- user intent parsing
- workflow choice
- user-facing expression
- artifact routing
- final report assembly
- conversation state

Does not own:

- source data mutation
- formula invention
- unsupported conclusions
- audit warning removal

### 4.2 Advisory Agent

Owns:

- user maturity detection
- analysis path design
- missing-data questioning
- beginner checklist mode
- expert collaboration mode
- next-best actions

Every response may include next-step suggestions, but visible suggestions must be at most three.

Prioritize:

1. Accuracy-improving data request.
2. Natural deeper analysis.
3. High-value deliverable action.

### 4.3 Data Foundation Agent

Owns:

- local-first source search
- statement extraction
- source lineage
- file fingerprint or stable metadata
- data type labeling
- three-statement validation
- data quality report

### 4.4 Financial Analysis Agent

Owns:

- metrics from approved evidence
- default and user-template mapping
- deep financial and operating analysis
- risks
- assumptions
- unsupported questions

It must use the Finance Rule Engine for fixed formulas where available.

### 4.5 Visualization Agent

Owns:

- chart selection
- chart specs
- dashboard structure
- infographic structure
- chart data references

It must not create new financial conclusions.

### 4.6 Audit Agent

Owns:

- read-only review
- `audit_report`
- `review_verdict`
- blocking decisions

It reviews both process and result.

## 5. Persistent Memory Model

To prevent cross-conversation loss, Hermes must maintain three levels of memory.

### 5.1 Product Memory

Shared across all users and all agents.

Contains:

- this contract
- default workflow
- schemas
- audit rules
- finance formulas
- chart rules
- disclosure rules

This is versioned and should be loaded for every report analysis workflow.

### 5.2 User Workspace Memory

Scoped to one user or one company workspace.

Contains:

- company name
- industry
- fiscal year convention
- currency and unit preference
- consolidation scope preference
- recurring report templates
- commonly used files or systems
- known private data dimensions
- preferred output style
- prior verified data sources

This memory may guide questions, but must not be treated as current-period evidence unless revalidated.

### 5.3 Conversation Memory

Scoped to one conversation or report task.

Contains:

- current user intent
- active period
- selected files
- current artifacts
- unresolved data gaps
- audit status
- final report state
- follow-up questions

This memory supports follow-up Q&A.

## 6. Memory Safety Rules

- Product memory can define rules.
- User workspace memory can define preferences and historical context.
- Conversation memory can define current task facts.
- Only current verified artifacts can support current financial conclusions.
- Historical user memory must never silently become source evidence.
- When using prior context, Hermes must disclose if it is a remembered preference rather than current verified data.

Example:

> 我会沿用你之前偏好的“老板汇报版”结构；本期数字仍以本次上传或本地识别的报表为准。

## 7. Cross-Agent Reuse

Future user-specific agents must not copy the whole prompt manually.

They should load:

1. Product Memory: shared report analysis scenario contract.
2. User Workspace Memory: user/company preferences.
3. Conversation Memory: current task state.
4. Tool/permission profile: allowed data sources and tools.

This ensures every dedicated agent follows the same workflow while adapting to the user.

## 8. User-Specific Agent Profile

Each dedicated user agent may have a profile:

```json
{
  "user_id": "string",
  "company_profile": {
    "company_name": "string|null",
    "industry": "string|null",
    "currency": "CNY",
    "default_unit": "万元",
    "fiscal_calendar": "calendar_year",
    "default_scope": "consolidated|null"
  },
  "report_preferences": {
    "language": "zh-CN",
    "style": "boss_report | management_review | audit_review | expert",
    "default_template": "default",
    "chart_preference": "standard"
  },
  "private_data_catalog": [
    {
      "name": "应收账款账龄表",
      "availability": "available | unavailable | unknown",
      "last_verified_at": "string|null",
      "use_cases": ["回款风险", "现金流质量"]
    }
  ],
  "permissions": {
    "local_files": true,
    "user_upload": true,
    "kingdee": false
  }
}
```

Profile data improves questioning and routing. It does not replace current evidence.

## 9. Handoff Consistency

All handoffs must include:

- scenario id: `report_analysis`
- contract version
- task id
- input artifact refs
- expected output artifact
- allowed tools
- audit trail id

Example:

```json
{
  "scenario_id": "report_analysis",
  "contract_version": "v1",
  "handoff_id": "build_analysis_pack",
  "from_agent": "orchestrator",
  "to_agent": "financial_analysis",
  "input_artifacts": ["financial_evidence_pack"],
  "expected_output_artifacts": ["analysis_pack"],
  "audit_trail_id": "string"
}
```

## 10. User-Facing Output

Formal report output is a complete finance report package. It must include:

- MaybeSheet report as the primary deliverable
- Sheet dashboard for key indicators and charts
- 财务分析报告
- 数据与计算审核报告
- 关键数据溯源摘要
- 限制事项
- 接下来你可以做什么, at most three suggestions

When delivered in MaybeSheet, these should be separate, clearly named pages/sections:

- `关键指标总览`
- `财务经营Dashboard`
- `深度分析报告`
- `数据与计算审核报告`
- `关键数据溯源摘要`
- `限制事项与下一步`

These are page/section names, not content depth standards. Do not treat the five-page MaybeSheet structure as permission to simplify the report.

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

When the product environment supports MaybeSheet, formal report output should default to a MaybeSheet report using SkillHub `global/maybeai-sheet@latest`.

Do not silently downgrade to local Excel, plain Markdown, or narrative-only output. Fallback is allowed only under the fallback protocol below.

Default MaybeSheet delivery is complete when:

- a MaybeSheet document URI or shareable reference exists
- the deep report sections are written into MaybeSheet
- the sheet dashboard and key indicator overview are included in MaybeSheet
- the data and calculation audit report is included
- the key data traceability summary is included
- the generated MaybeSheet is read back or otherwise verified

If MaybeSheet write or verification fails because of permission, missing tool, missing template, or system error, Hermes may provide a fallback output only after:

1. clearly stating that the MaybeSheet version has not been generated yet
2. explaining the concrete failure reason and the next step needed to generate MaybeSheet
3. delivering the same report content in the best available fallback format, such as MaybeSheet-readable Markdown, local spreadsheet, or structured text
4. marking the delivery status as `临时交付，待生成 MaybeSheet`

Never claim that a fallback output is the final MaybeSheet report.

One-page infographic and PPT are optional exports, not default first delivery. After delivering MaybeSheet, Hermes may ask whether the user wants:

- a one-page visual exported with `global/infographic-report@latest`
- an editable slide deck exported with `global/ppt-report@latest`

Do not generate these by default unless the user requested them.

The default sheet dashboard should summarize:

- core financial indicators
- period-over-period comparison
- budget/target comparison when available
- industry or peer comparison when available
- key risk signals
- clear status labels such as 改善, 承压, 异常, 待补充

Inputs to dashboard/export skills should come from reviewed evidence, reviewed analysis, and reviewed visualization data. They must not introduce new financial conclusions or unaudited numbers.

If budget, industry, or peer benchmarks are unavailable, do not fabricate them. Use available period comparison and disclose the missing benchmark data.

Do not show internal agent names.

## 10.1 Quality Non-Regression

Report quality must move forward, not backward.

If a previous report, reference output, or known good template contains richer analysis, charts, or structure, use it as the minimum quality baseline and enrich it. Do not replace it with a thinner report.

Deep analysis is not satisfied by renaming a sheet to `深度分析报告` and listing short narrative blocks. A formal deep report must contain multi-dimensional, evidence-backed financial and operating analysis.

Minimum deep report dimensions:

- 管理层摘要：结论、财务主线、经营观察、关键风险
- 季度核心财务指标：收入、毛利、净利润、现金流、资产负债率、费用、研发投入
- 财务分析图表：收入/利润/现金流趋势、净利率/负债率趋势、费用结构、利润与现金流漏斗或桥接
- 经营观察：结合经营类指标或模拟经营数据时，必须标明数据性质和验证边界
- 财务经营联动判断：收入增长、利润质量、现金质量、费用投入、经营效率之间的关系
- 风险与建议：数据范围、利润质量、费用效率、现金质量、经营验证建议
- 审核报告和溯源摘要：不能省略

Audit should flag the report as needing improvement if these dimensions are missing.

## 10.2 Skill Composition

Use stable skills and reusable capabilities for production workflow steps. Do not hand-code report generation, dashboards, or infographic rendering during a normal analysis run unless the goal is explicitly prototyping or creating a missing skill.

Required skill responsibilities:

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

End-to-end sequence:

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

If a necessary workflow step lacks a stable skill, propose or create the missing skill. Do not repeatedly solve the same production workflow with one-off coding.

It is acceptable to mention:

> 本报告已完成数据来源核验、三表完整性核验、指标计算复核、图表一致性复核和结论支撑性检查。

## 11. First Build Checklist

1. Implement scenario loading: `report_analysis`.
2. Implement product memory loading.
3. Implement user workspace profile read/write.
4. Implement conversation artifact state.
5. Implement handoff allowlist.
6. Implement artifact schemas.
7. Implement audit trail ids.
8. Implement user-visible audit report.
9. Implement next-best-action generation with max three suggestions.

## 10.3 Boss-Review Default Template（老板审阅默认模板）

For boss-review style formal reports, the default MaybeSheet output MUST use the 9 front-sheet template published at `https://www.maybe.ai/docs/spreadsheets/d/6a1d15393638526b20e3b4df`. Each sheet has a fixed column schema; do not invent new column names. Every data row MUST carry a management/observation column (管理观察 / 管理说明 / 判断 / 建议 / etc.); bare numbers without management meaning are rejected by the output contract.

The 9 front sheets and their column schemas are:

1. **封面** — columns: `项目` / `内容` / `辅助项目` / `辅助内容`
   - Required rows: 公司, 报告名称, 报告模板, 数据口径, 核心结论
   - Companion rows: 报告期间, 报告用途, 金额单位, 生成日期, 阅读顺序

2. **老板摘要** — columns: `模块` / `管理层结论（事实+数字）` / `决策提示（管理含义）`
   - 5 fixed modules: 总体表现, 增长质量, 现金质量, 偿债结构, 管理动作

3. **经营概览** — columns: `项目` / `本次观察（数据事实）` / `管理说明（业务含义）`
   - 6 fixed rows: 财务表现, 收入趋势, 盈利趋势, 现金状态, 费用效率, 经营数据说明

4. **利润分析** — columns: `指标` / `一季度` / `二季度` / `三季度` / `四季度` / `全年` / `分析口径`
   - Required indicators: 营业收入, 营业成本, 毛利, 毛利率, 销售费用, 研发费用, 管理费用, 财务费用, 营业利润, 净利润, 净利率

5. **资产负债分析** — columns: `一季度末` / `二季度末` / `三季度末` / `四季度末` / `指标` / `管理观察`
   - Required indicators: 货币资金, 应收账款, 流动资产合计, 资产总计, 应付账款, 流动负债合计, 负债合计, 所有者权益合计, 资产负债率

6. **现金流分析** — columns: `指标` / `Q1` / `Q2` / `Q3` / `Q4` / `全年/期末` / `管理观察`
   - Required indicators: 经营现金流, 净利润, OCF/净利润, 期末现金余额

7. **关键指标** — columns: `一季度` / `二季度` / `三季度` / `四季度` / `全年/期末` / `指标`
   - Required indicators: 营业收入, 毛利, 毛利率, 营业利润, 净利润, 净利率, 经营现金流, 期末货币资金, 资产总计, 资产负债率

8. **风险与建议** — columns: `类型` / `事项` / `判断` / `建议`
   - At least 5 entries: 数据范围, 利润质量, 现金质量, 偿债结构, 管理跟进

9. **追问支持** — columns: `可追问主题` / `可追溯依据` / `可下钻字段` / `需要补充资料`
   - At least 5 directions: 收入与利润趋势, 费用结构, 资产和偿债能力, 现金流质量, 经营数据缺口

Sheet header names are case-sensitive and order-sensitive. The MaybeSheet write helper `global/maybeai-sheet@latest` matches columns by header name in sequence. Reordering or renaming columns is a contract violation.

The cover page MUST carry 公司/报告期间/币种/单位/口径/生成日期. Limitations such as 演示用模拟数据 or 经营数据暂未提供 MUST be visible in the cover, 经营概览, 风险与建议, and 追问支持 sheets — silent omission is forbidden.

When the product environment supports MaybeSheet, this template is the default. The general 5-page structure described in §10 remains the audit/traceability/limitations/next-step frame; the 9 front sheets here are the **content** the front of the report follows. The two layers compose: the 9 front sheets live on top, the audit / traceability / limitations / next-step pages live behind them.

This 10.3 section supersedes any softer instruction in the rest of this contract about default front-sheet naming whenever the user requests a boss-review style formal report and has not specified a different template.
