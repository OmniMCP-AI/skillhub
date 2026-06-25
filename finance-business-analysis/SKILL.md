---
name: finance-business-analysis
description: "Generate management-ready financial and business analysis reports from user-provided templates, financial statements, budgets, and operating data. Use when users need monthly, quarterly, or annual financial/business review reports, template mapping, metric filling, variance analysis, and report output in Excel, Word, PDF, or MaybeAI Sheet."
---

# Financial Business Analysis

Generate management-ready financial and business analysis reports from templates, financial statements, budgets, and operating data.

## Use When

- The user asks for a monthly, quarterly, or annual financial or business analysis report.
- The user provides an Excel or Word analysis template plus source data.
- The user wants finance or operating data mapped into an existing management report format.
- The task involves metric mapping, period comparison, variance analysis, or narrative report drafting.

## Inputs

- Optional report template in Excel or Word format.
- Finance, operating, budget, or KPI data in Excel, CSV, or other local exports.
- Target period and reporting cadence.
- Optional output preference such as Excel, Word, PDF, Markdown, or MaybeAI Sheet.

## Workflow

1. Identify the entity, period, report goal, available source files, and template source.
2. Parse the template structure: metrics, sections, dimensions, period columns, formulas, and chart areas.
3. Inspect source data: worksheets, columns, date ranges, units, missing values, and data quality issues.
4. Map template fields to source data by exact match, semantic match, or calculated derivation.
5. Mark unsupported fields as data gaps instead of inventing values.
6. Calculate metrics such as current period, cumulative period, variance, ratio, trend, and contribution.
7. Generate concise management commentary that separates facts, calculations, inferences, and recommendations.
8. Write the report to the requested output surface and keep source references for follow-up.

## Output Requirements

- A filled report or sheet-ready report structure.
- A data quality summary.
- A template mapping table with mapped fields and gaps.
- Analysis notes for major movements, risks, and management follow-up.
- Source references that support later follow-up questions.

## Rules

- Do not invent operating data, budget figures, or prior-period values.
- Keep real source data, synthetic demo data, and missing data clearly separated.
- Preserve the user's template when one is provided.
- If no template is provided, use a practical management-review structure.
- Keep public-facing skill documentation in English.
