# MaybeAI Sheet — Template Column Headers & API Behavior

Discovered 2026-06 via direct API reads of the boss-review-generic template (document_id `6a1810b906632ed57e0b2946`).

**Rule: Always `read_sheet` the target sheet before writing. This reference is for quick lookup and cross-validation only.**

## Critical: `read_sheet` Returns Dicts

`POST /api/v1/excel/read_sheet` returns each row as a **dictionary** keyed by column name, NOT a list:

```json
{
  "success": true,
  "data": [
    {"指标": "营业收入", "一季度": "1180000", "二季度": "980000", ...},
    {"指标": "营业成本", "一季度": "295000", "二季度": "290000", ...}
  ]
}
```

When building `update_range` payloads, extract column names from `data[0].keys()` and preserve their left-to-right order.

## Boss Review Template Column Headers (confirmed 2026-06)

### 利润分析
- **Columns (7):** `指标 | 一季度 | 二季度 | 三季度 | 四季度 | 全年 | 分析口径`
- **Note:** Use `一季度` NOT `Q1`; `二季度` NOT `Q2`

### 资产负债分析
- **Columns (6):** `指标 | 一季度末 | 二季度末 | 三季度末 | 四季度末 | 管理观察`
- **Note:** Column 6 is `管理观察` (no 全年 column)

### 现金流分析
- **Columns (8):** `指标 | Q1 | Q2 | Q3 | Q4 | 全年 | 期末 | 管理观察`
- **Note:** Uses `Q1/Q2/Q3/Q4` (different from 利润分析 which uses 一季度/二季度/三季度/四季度)

### 关键指标
- **Columns (7):** `指标 | 一季度 | 二季度 | 三季度 | 四季度 | 全年 | 期末`
- **Sub-sections:** 核心指标 (rows 1-10) + BI 经营看板 (rows 11+)
- **Note:** `期末` column (column 7) — not present in 利润分析

### 老板摘要
- **Columns (3):** `模块 | 管理层结论 | 决策提示`
- **Type:** row-based (5 modules: 收入/盈利/现金流/运营/战略)
- **Note:** 3 columns only — NO period columns

### 经营概览
- **Columns (3):** `项目 | 本次观察 | 管理说明`
- **Type:** row-based
- **Note:** 3 columns (not 2)

### 风险与建议
- **Columns (3):** `事项 | 判断 | 建议`
- **Type:** row-based

### 追问支持
- **Columns (3):** `可下钻字段 | 需要补充资料 | 可追溯依据`
- **Type:** row-based

### 封面
- **Columns (4):** `项目 | 内容 | 辅助项目 | 辅助内容`
- **Type:** row-based

## `update_range` Column-Matching Behavior (critical)

The MaybeAI `update_range` API performs column routing **by matching header names**, not cell positions. Discovered through controlled write/read comparison on `6a1d48ee8bcbcda2aba7e8e6`.

**Rules:**

1. **Write the header row as row 1** — the header defines column mapping for all subsequent rows.
2. **Each data row's first element = actual value** — never empty, never the column name.
   - ✅ Correct: `["营业收入","1180000","980000","780000","580000","3520000","利润表本期金额"]`
   - ❌ Wrong: `["指标","1180000","980000",...]` — "指标" goes into column A, data shifts right
   - ❌ Wrong: `["","营业收入","980000",...]` — empty first cell misaligns all columns
3. **Header names must match exactly** — `一季度` ≠ `Q1`, `二季度末` ≠ `Q2end`. Read the template first.
4. **Column order matters** — the API matches names in left-to-right sequence. `[Q1,Q2,Q3,Q4]` written against header `[一季度,二季度,三季度,四季度]` misaligns even with identical label sets.
5. **Range must be horizontal** — `"A1:G14"` ✅; `"A1:A14"` ❌ (vertical ranges return HTTP 400).

## Common Write Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Empty first cell in data row | All columns shift right by 1 | First element = actual value |
| Header name typo | Data lands in wrong columns | `read_sheet` template first |
| `Q1` vs `一季度` | Mismatch | Match template exactly |
| Skipping header row | All data misaligned | Include header row every write |
| >12 rows per call | HTTP 500 | Split into batches ≤12 rows |
| Single-cell range | HTTP 400 | Minimum 1 row × 2 columns |

## Reliable Write Sequence

```python
# 1. Read template to get exact header names and order
r = api('/api/v1/excel/read_sheet', {'uri': uri, 'worksheet_name': '利润分析'})
header_row = list(r['data'][0].keys())  # preserves left-to-right order

# 2. Build payload: header row + data rows
rows = [header_row]  # header must be row 1
for item in data:
    rows.append([item['name'], str(item['q1']), ..., item['note']])

# 3. Write ≤12 rows at a time
wr("利润分析", f"A1:G{len(rows)}", rows)
```
