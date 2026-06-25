# Field alias and report read-back pitfalls

Session-derived durable lesson for Kingdee-like three-statement outputs.

## Symptom

A foundation run can pass blocking validation while downstream report fields are still incomplete or wrong because the source statement uses non-canonical item labels.

Examples seen in Shanghai Yunleng demo statements:

- Profit statement used `研究费用`, while report logic expected `研发费用`.
- Balance sheet used `所有者权益（或股东权益）合计`, while report logic expected `所有者权益合计` or `股东权益合计`.
- Net profit row used `四：净利润（净亏损以"-"号填列）`, with a Chinese colon and suffix, so exact matching for `净利润` can miss it.

## Required handling pattern

When deriving report metrics from `statement_facts.json` or raw workbook rows:

1. Prefer canonical keys from the foundation outputs when available.
2. If any management-report key field is null, blank, or suspiciously zero, inspect the raw source rows before final delivery.
3. Match financial statement row labels by normalized containment/alias sets, not exact string only.
4. At minimum include these aliases:
   - R&D expense: `研发费用`, `研究费用`
   - Equity total: `所有者权益合计`, `股东权益合计`, `所有者权益（或股东权益）合计`
   - Net profit: any row containing `净利润`
   - Operating profit: any row containing `营业利润`
   - Profit total: any row containing `利润总额`
5. Re-run generation after alias fixes and read back the affected workbook/sheet/range.

## Verification expectation

Before delivering a financial report, verify at least:

- The Excel/Sheet exists and contains expected user-facing sheets.
- Key rows in `利润分析` are non-empty and reasonable: revenue, R&D expense, operating profit, net profit.
- Key rows in `资产负债分析` are non-empty and reasonable: assets, liabilities, equity, asset-liability ratio.
- Data boundary labels remain correct: demo paths are user-facing `演示用模拟数据`; missing operating data is user-facing `数据暂未提供`.
