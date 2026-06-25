---
name: finclaw-three-statement-foundation
description: Parse, validate, normalize, and analyze Kingdee-like Q1-Q4 financial statements for FinClaw. Use when the user provides profit statements, balance sheets, and cash-flow statements and needs a grounded three-statement fact base, data quality checks, template mapping support, report draft inputs, or follow-up Q&A evidence. Handles period/company/type validation, balance and cash tie-outs, current vs YTD vs point-in-time amount types, and outputs reviewable JSON/CSV/Markdown artifacts.
---

# FinClaw Three-Statement Foundation

This skill provides the deterministic foundation for FinClaw financial analysis.

## Use When

Use this skill when the task involves:

- Kingdee-like exported financial statements,
- Q1-Q4 profit statements, balance sheets, and cash-flow statements,
- three-statement parsing and validation,
- source-traceable normalized facts,
- financial report drafts grounded in the same data,
- backtest validation against expected results.

## Core Rule

Do not generate a formal report when there is a blocking data issue.

Blocking issues include:

- requested period does not match file period or sheet date,
- company names differ across files,
- statement type does not match the expected file,
- target quarter files are missing,
- balance sheet does not balance,
- cash-flow ending cash does not tie to balance sheet cash.

**Path resolution**: `search_files` results may show paths under `/usr/local/lib/hermes-agent/` but actual files are under `/root/`. If the script fails with `FileNotFoundError`, run `find / -name "<filename>" 2>/dev/null` to resolve the actual path, then pass the correct `--input-dir`.

Warnings may still allow draft output, but must be listed in the result.

## Amount-Type Rules

- Profit statement: `current` = 本期金额, `ytd` = 本年累计金额.
- Cash-flow statement: `current` = 本期金额, `ytd` = 本年累计金额.
- Balance sheet: `ending` = 期末余额, `beginning` = 年初余额. It is point-in-time and has no quarterly current amount.

## Profit Alias Backstop

After running the foundation script, do not rely on `quarter_metrics.json` alone when profit fields are unexpectedly `null` or when generated report read-back shows implausible zero values for metrics that should exist. If revenue and expense fields parse but `operating_profit`, `net_profit`, `net_profit_ytd`, or R&D expense are null/zero, immediately read the original profit statement rows and match common aliases before drafting any report:

- `二、营业利润（亏损以"-"号填列）` → operating profit
- `三、利润总额（亏损总额以"-"号填列）` → total profit
- `四：净利润（净亏损以"-"号填列）` and `四、净利润（净亏损以"-"号填列）` → net profit
- `研究费用` may be the source label for research/R&D expense

Use the source-row values only when the company, period, and statement type have already passed validation. Disclose the alias backstop in the audit report as a calculation/source review note, not as a blocking failure.

## Report Read-Back Sanity Gate

After generating any Excel/MaybeAI management report from parsed statements, read back representative cells from the front sheets before delivery. At minimum verify:

- `老板摘要` does not show net profit, operating profit, or OCF/净利润 as `0`/`0.00%` when the source profit/cash-flow statements contain non-zero values.
- `利润分析` has non-zero rows for net profit, operating profit, and research/R&D expense when those rows exist in the source statement under aliases.
- `底稿_数据校验` ties financial revenue to operating/contract revenue where operating data is present, and any real difference is described as a口径差异 rather than silently ignored.
- Demo/mock packs are explicitly marked in `封面`, `经营概览`, `风险与建议`, and `追问支持`; do not let a technically valid workbook hide the synthetic-data limitation.

If read-back finds a likely mapping miss, fix the alias/mapping and regenerate before uploading or sharing the workbook.

## Prerequisites

This skill requires `openpyxl`. Install it if missing:

```bash
# Debian/Ubuntu
apt-get install -y python3-openpyxl

# Or via pip (if pip is available)
python3 -m pip install openpyxl
```

## Workflow

1. Collect input files or an input directory.
2. Run `scripts/run_three_statement_foundation.py`.
3. Inspect `validation_issues.json`.
4. If there are no blocking errors, use generated artifacts for downstream skills:
   - report writing,
   - MaybeAI Sheet rendering,
   - charting,
   - grounded follow-up Q&A.

## Command

```bash
python3 scripts/run_three_statement_foundation.py \
  --input-dir /path/to/financial-statements \
  --out-dir /path/to/output \
  --expected-year 2025
```

Optional:

```bash
python3 scripts/run_three_statement_foundation.py \
  --input-dir /path/to/financial-statements \
  --out-dir /path/to/output \
  --expected-year 2025 \
  --expected-company "上海云棱智能科技有限公司" \
  --expected-results /path/to/expected-results.json
```

## Outputs

The script writes:

- `manifest.json`: input files, detected metadata, output paths.
- `validation_issues.json`: blocking errors, warnings, and info items.
- `statement_facts.json`: normalized source-traceable facts.
- `statement_facts.csv`: flat facts for sheet tools.
- `quarter_metrics.json`: key metrics by quarter.
- `analysis_summary.json`: derived trend, tie-out, and quality analysis.
- `report_draft.md`: concise boss-review draft.
- `followup_examples.json`: sample grounded Q&A evidence.
- `backtest_results.json`: present only when `--expected-results` is supplied.

## References

- **`references/statement_facts_format.md`** — Actual JSON format (list of objects, not dict), canonical key availability, YTD→quarterly conversion, balance sheet raw-row extraction, and complete extraction code sample. **Read this before writing any code that reads `statement_facts.json`.**
- **`references/report_generation.md`** — openpyxl 技术指南：Font 参数（color 而非 fc）、合并单元格陷阱（只写主单元格）、PatternFill fgColor、货币/百分比格式函数、多表 Excel 报告模板结构、封面页 SYNTHETIC_DEMO_DATA 标注规范。**生成 Excel 报告前必读。**
- **`references/field-alias-pitfalls.md`** — Field-alias and read-back pitfalls from report generation: handle labels such as `研究费用`, `所有者权益（或股东权益）合计`, and `四：净利润...`; verify affected report rows after alias fixes.

## Downstream Composition

Recommended downstream skills:

- `global/maybeai-sheet` for MaybeAI Sheet output.
- `data-reporting/bi-analysis` or `global/bi-analysis` for generic BI views.
- `comprehensive-finance/finance-business-analysis` for template-driven report generation.
- `global/wtt-fin-chart` for charts and dashboards.
- `data-reporting/finclaw-mock-data` only for testing, backtest, or demo validation. It is not a required part of the customer-facing product flow.
