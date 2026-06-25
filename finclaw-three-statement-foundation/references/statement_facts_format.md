# statement_facts.json — Actual Format & Usage Guide

## ⚠️ Critical: The JSON is a list of objects, not a dict

The output is a **flat list of ~920 rows**, NOT a dict keyed by company/period:

```json
[
  {
    "company": "上海云棱智能科技有限公司",
    "period": "Q1",
    "period_type": "year_to_date",
    "statement_type": "profit_statement",
    "line_item_raw": "一、营业收入",
    "line_item_canonical": "revenue",
    "amount_type": "ytd",
    "amount": 980000.0,
    "unit": "元",
    "source": { "file": "...", "sheet": "...", "row": 4, "column": "..." },
    "quality_flags": []
  },
  ...
]
```

**Wrong**: `facts["revenue"]["Q1"]` → `TypeError: list indices must be integers`
**Correct**: Pivot the list into a dict-of-dict (see below).

## Pivot Pattern

```python
import json
from collections import defaultdict

with open("statement_facts.json") as f:
    rows = json.load(f)

by_key = defaultdict(lambda: defaultdict(list))
for r in rows:
    if r["amount"] is not None:
        by_key[r["line_item_canonical"]][r["period"]].append(r["amount"])

def get(key, period):
    vals = by_key[key].get(period, [None])
    return vals[0] if vals[0] is not None else 0
```

## Canonical Key Availability — Check manifest, not assumptions

The canonical key availability table varies by company/format. **Do NOT assume a key is absent — always check the actual extraction results.**

Verified for `demo-上海云棱智能科技有限公司` (Kingdee export, Q1–Q4 2025):

| Canonical Key | Q1 | Q2 | Q3 | Q4 | Notes |
|---|---|---|---|---|---|
| `revenue` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `net_profit` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `operating_profit` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `operating_cash_flow` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `ending_cash` | ✓ | ✓ | ✓ | ✓ | Point-in-time |
| `management_expense` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `research_expense` | ✓ | ✓ | ✓ | ✓ | YTD cumulative |
| `assets_total` | ✓ | ✓ | ✓ | ✓ | Extracted via BS point-in-time row |
| `liabilities_total` | ✓ | ✓ | ✓ | ✓ | Extracted via BS point-in-time row |
| `equity_total` | ✓ | ✓ | ✓ | ✓ | Extracted via BS point-in-time row |
| `gross_profit` | ✗ | ✗ | ✗ | ✗ | Not present — compute from revenue and cost rows |
| `net_margin` | ✗ | ✗ | ✗ | ✗ | Not a canonical key — compute as net_profit / revenue |

**Before assuming a key is missing, check `manifest.json` and `quarter_metrics.json`** in the output directory. These reflect what was actually extracted.

## YTD → Quarterly Conversion

Profit/cash-flow amounts are **YTD cumulative** (本年累计):
- Q1 YTD = Q1 actual
- Q2 YTD = Q1+Q2 cumulative → Q2 solo = YTD_Q2 − YTD_Q1
- Q3 YTD = Q1+Q2+Q3 cumulative → Q3 solo = YTD_Q3 − YTD_Q2
- Q4 YTD = Q1+Q2+Q3+Q4 cumulative → Q4 solo = YTD_Q4 − YTD_Q3

```python
def ytd_to_quarterly(series_dict):
    """Convert YTD cumulative {period: amount} to quarterly solo list."""
    q1 = series_dict.get("Q1") or 0
    q2 = (series_dict.get("Q2") or 0) - q1
    q3 = (series_dict.get("Q3") or 0) - (series_dict.get("Q2") or 0)
    q4 = (series_dict.get("Q4") or 0) - (series_dict.get("Q3") or 0)
    return [q1, q2, q3, q4]   # in yuan, convert to 万元 after

# Usage:
rev = [round(v/10000, 2) for v in ytd_to_quarterly(by_key["revenue"])]
# → [98.0, 123.0, 151.0, 178.0]  (Q1-Q4 solo, 万元)
```

## Balance Sheet: Raw Row Extraction

BS canonical keys (`assets_total`, `liabilities_total`, `equity_total`) ARE populated by the extraction script from balance sheet rows. Extract them like profit statement keys:

```python
def bs_key(keyword, period):
    for r in rows:
        if keyword in r["line_item_raw"] and r["period"] == period:
            return r["amount"] or 0
    return 0

# Extract by quarter (point-in-time)
astr = [round(bs_key("资产总计", p) / 10000, 2) for p in ["Q1","Q2","Q3","Q4"]]
liab = [round(bs_key("负债合计", p) / 10000, 2) for p in ["Q1","Q2","Q3","Q4"]]
eqt  = [round(bs_key("所有者权益（或股东权益）合计", p) / 10000, 2)
        for p in ["Q1","Q2","Q3","Q4"]]

# Verify: assets = liabilities + equity
for i, p in enumerate(["Q1","Q2","Q3","Q4"]):
    diff = round(astr[i] - liab[i] - eqt[i], 2)
    assert abs(diff) < 0.01, f"BS does not balance at {p}: {diff}"
```

## Unit Convention

All amounts in `statement_facts.json` are in **元 (yuan)**.
Convert to **万元 (10,000 yuan)** before writing to templates:

```python
w = lambda v: round(v / 10000, 2) if v else 0
```

## Complete Extraction Example

```python
import json
from collections import defaultdict

with open("statement_facts.json") as f:
    rows = json.load(f)

by_key = defaultdict(lambda: defaultdict(list))
for r in rows:
    if r["amount"] is not None:
        by_key[r["line_item_canonical"]][r["period"]].append(r["amount"])

def ytd_q(key):
    s = by_key.get(key, {})
    q1 = s.get("Q1") or 0; q2 = s.get("Q2") or 0
    q3 = s.get("Q3") or 0; q4 = s.get("Q4") or 0
    return [round(q1/10000,2), round((q2-q1)/10000,2),
            round((q3-q2)/10000,2), round((q4-q3)/10000,2)]

def bs_q(keyword):
    vals = [round(bs_key(keyword, p) / 10000, 2) for p in ["Q1","Q2","Q3","Q4"]]
    return vals

rev  = ytd_q("revenue")
ntpr = ytd_q("net_profit")
oprp = ytd_q("operating_profit")
ocf  = ytd_q("operating_cash_flow")
mngp = ytd_q("management_expense")
rsrp = ytd_q("research_expense")
gros = [round((by_key["revenue"].get(p,0) - by_key.get("operating_cost",{}).get(p,0))/10000, 2)
        for p in ["Q1","Q2","Q3","Q4"]]
eash = [round((by_key["ending_cash"].get(p) or 0)/10000, 2) for p in ["Q1","Q2","Q3","Q4"]]
astr = bs_q("资产总计")
liab = bs_q("负债合计")
eqt  = bs_q("所有者权益（或股东权益）合计")

# Totals (sum of quarters, NOT YTD values)
rev_t  = round(sum(rev),  2)
ntpr_t = round(sum(ntpr), 2)
ocf_t  = round(sum(ocf),  2)
```
