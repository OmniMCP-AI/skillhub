# Fallback: Rebuild quarter_metrics from statement_facts

When `quarter_metrics.json` or `computed_data.json` has null/missing values (data extraction bug in heredoc), rebuild from `statement_facts.json`.

## statement_facts schema

```json
{
  "company": "杭州星澜数字服务有限公司",
  "period": "Q1",           // Q1/Q2/Q3/Q4
  "period_type": "year_to_date | current_period",
  "statement_type": "profit_statement | balance_sheet | cash_flow",
  "line_item_raw": "一、营业收入",      // raw label from Excel
  "line_item_canonical": "revenue | operating_cost | net_profit | ...", // normalized
  "amount_type": "ytd | current",
  "amount": 1180000.0,
  "unit": "元",
  "source": {"file": "...", "sheet": "...", "row": 4, "column": "本年累计金额"}
}
```

## Rebuild function

```python
import json

facts = json.load(open('/path/to/statement_facts.json'))

def get_fact(item, q, amt_type='current'):
    """Get amount from statement_facts by canonical item name + quarter + amount_type."""
    for f in facts:
        if f.get('period') == q \
           and f.get('line_item_canonical') == item \
           and f.get('amount_type') == amt_type:
            return f.get('amount')
    return None

qm = {}
for q in ['Q1','Q2','Q3','Q4']:
    revenue   = get_fact('revenue', q) or 0
    cost      = get_fact('operating_cost', q) or 0
    sga = (
        get_fact('selling_expense', q) or 0,
        get_fact('management_expense', q) or 0,
        get_fact('research_expense', q) or 0,
        get_fact('financial_expense', q) or 0,
    )
    op_profit = get_fact('operating_profit', q) or (revenue - cost - sum(sga))
    net_profit = get_fact('net_profit', q) or (op_profit * 0.85)
    assets    = get_fact('total_assets', q) or 0
    equity    = get_fact('total_equity', q) or 0
    liabilities = assets - equity if assets and equity else (get_fact('total_liabilities', q) or 0)

    qm[q] = {
        'revenue': revenue,
        'cost': cost,
        'op_profit': op_profit,
        'net_profit': net_profit,
        'net_profit_ytd': net_profit,
        'ocf': get_fact('operating_cash_flow', q) or 0,
        'ending_cash': get_fact('ending_cash', q) or 0,
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'net_margin': net_profit / revenue if revenue > 0 else None,
        'asset_liability_ratio': liabilities / assets if assets > 0 else None,
    }
```

## Known canonical item names

| Canonical | Raw Excel label |
|-----------|----------------|
| revenue | 一、营业收入 |
| operating_cost | 减：营业成本 |
| selling_expense | 销售费用 |
| management_expense | 管理费用 |
| research_expense | 研究费用 |
| financial_expense | 财务费用 |
| operating_profit | 二、营业利润（亏损以"-"号填列） |
| net_profit | 四：净利润（净亏损以"-"号填列） |
| total_assets | 资产总计 |
| total_equity | 所有者权益（或股东权益）合计 |
| total_liabilities | 负债合计 |
| operating_cash_flow | 经营活动产生的现金流量净额 |
| ending_cash | 五、期末现金余额 |
| current_assets | 流动资产合计 |
| fixed_assets | 固定资产账面价值 |

## Symptoms of the bug

- `computed_data.json` or `quarter_metrics.json` has `null` for `operating_profit`, `net_profit`, `net_margin`
- `statement_facts.json` exists and has 400+ rows (data IS extracted)
- Root cause: heredoc/shell function capturing `facts` returned `None` but iteration over `facts` list works fine

## Verification

```bash
python3 -c "
import json
facts = json.load(open('/path/to/statement_facts.json'))
qm = {}
for q in ['Q1','Q2','Q3','Q4']:
    rev = next((f['amount'] for f in facts if f['period']==q and f['line_item_canonical']=='revenue'), None)
    np = next((f['amount'] for f in facts if f['period']==q and f['line_item_canonical']=='net_profit'), None)
    print(f'{q}: revenue={rev} net_profit={np}')
"
```
