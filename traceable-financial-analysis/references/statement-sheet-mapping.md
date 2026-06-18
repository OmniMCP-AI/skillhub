# Statement Sheet Mapping

The 12 raw sheets (3 statements × 4 quarters) all use a normalized 4-column structure. Account names are in column A; row indices are the canonical references for downstream formulas.

## Sheet naming convention

- `利润表-2025Q1` ... `利润表-2025Q4` (4 sheets)
- `资产负债表-2025Q1` ... `资产负债表-2025Q4` (4 sheets)
- `现金流量表-2025Q1` ... `现金流量表-2025Q4` (4 sheets)

## Common 4-column structure

| Col | Header | Notes |
|-----|--------|-------|
| A | 项目 | Account name (Chinese) |
| B | 行次 | Line number (Kingdee style) |
| C | Varies by statement | See per-statement below |
| D | Varies by statement | See per-statement below |

**Critical**: Rows 1-3 are headers (title / 编制单位 / column headers). Data starts at row 4.

## 利润表 (PL) — column meaning

| Col | Header | Meaning |
|-----|--------|---------|
| C | 本年累计金额 | YTD amount (for Q1 = Q1 amount; for Q4 = FY amount) |
| D | 本期金额 | Quarter-only amount (the "季度环比" source) |

**Row map** (canonical, used by 利润分析 formulas):

| Row | Account |
|-----|---------|
| 2 | 一、营业收入 |
| 3 | 减：营业成本 |
| 4 | 减：税金及附加 |
| 5 | 减：销售费用 |
| 6 | 减：管理费用 |
| 7 | 减：研发费用 |
| 8 | 减：财务费用 |
| 9 | 加：其他收益 |
| 10 | 加：投资收益 |
| 11 | 加：公允价值变动收益 |
| 12 | 二、营业利润 |
| 13 | 加：营业外收入 |
| 14 | 三、利润总额 |
| 15 | 减：所得税费用 |
| 16 | 四、净利润 |

**Formula reference convention**: 利润分析 Q1-Q4 columns use D column (本期金额). 利润分析 F column (全年) uses `=SUM(B:E)`.

## 资产负债表 (BS) — column meaning

| Col | Header | Meaning |
|-----|--------|---------|
| C | 期末余额 | Period-end balance (the point-in-time snapshot) |
| D | 年初余额 | Year-start balance (FY2024 12-31, same for all 4 quarters) |

**Row map**:

| Row | Account |
|-----|---------|
| 2 | 货币资金 |
| 3 | 应收账款 |
| 4 | 存货 |
| 5 | 预付款项 |
| 6 | 其他流动资产 |
| 7 | 流动资产合计 |
| 8 | 固定资产 |
| 9 | 在建工程 |
| 10 | 无形资产 |
| 11 | 长期待摊费用 |
| 12 | 其他非流动资产 |
| 13 | 非流动资产合计 |
| 14 | 资产总计 |
| 15 | 短期借款 |
| 16 | 应付账款 |
| 17 | 预收款项 |
| 18 | 应付职工薪酬 |
| 19 | 应交税费 |
| 20 | 其他流动负债 |
| 21 | 流动负债合计 |
| 22 | 长期借款 |
| 23 | 递延收益 |
| 24 | 其他非流动负债 |
| 25 | 负债合计 |
| 26 | 实收资本 |
| 27 | 资本公积 |
| 28 | 盈余公积 |
| 29 | 未分配利润 |
| 30 | 所有者权益合计 |

**Formula reference convention**: 资产负债分析 B-E columns use C column (期末余额). NO F column (point-in-time data, no sum).

## 现金流量表 (CF) — column meaning

| Col | Header | Meaning |
|-----|--------|---------|
| C | 本期金额 | Quarter-only amount |
| D | 本年累计金额 | YTD amount (for Q1=Q1, for Q4=FY) |

**Row map**:

| Row | Account |
|-----|---------|
| 2 | 销售商品、提供劳务收到的现金 |
| 3 | 收到的税费返还 |
| 4 | 收到其他与经营活动有关的现金 |
| 5 | 经营活动现金流入小计 |
| 6 | 购买商品、接受劳务支付的现金 |
| 7 | 支付给职工以及为职工支付的现金 |
| 8 | 支付的各项税费 |
| 9 | 支付其他与经营活动有关的现金 |
| 10 | 经营活动现金流出小计 |
| 11 | 经营活动产生的现金流量净额 |
| 12 | 收回投资收到的现金 |
| 13 | 取得投资收益收到的现金 |
| 14 | 投资活动现金流入小计 |
| 15 | 购建固定资产、无形资产和其他长期资产支付的现金 |
| 16 | 投资支付的现金 |
| 17 | 其他投资活动现金流出 |
| 18 | 投资活动现金流出小计 |
| 19 | 投资活动产生的现金流量净额 |
| 20 | 吸收投资收到的现金 |
| 21 | 取得借款收到的现金 |
| 22 | 偿还债务支付的现金 |
| 23 | 筹资活动产生的现金流量净额 |
| 24 | 现金及现金等价物净增加额 |
| 25 | 期末现金及现金等价物余额 |

**Formula reference convention**: 现金流分析 B-E columns use C column (本期金额). 现金流分析 F column (全年) uses `=SUM(B:E)`.

## Pitfalls when parsing Kingdee raw xlsx

1. **Header rows vary**: Some Kingdee exports have 2 header rows, some have 3. Don't hardcode "skip 3" — instead, find the row where col A == "项目" and start data from row+1.

2. **Subtotal lines have empty A col**: Rows like "一、营业收入" (group header) have A=label but B/C/D empty. Skip these in the row_map.

3. **Q1 vs FY semantics**: For PL and CF, "本年累计金额" for Q1 == "本期金额" (only one month elapsed). For Q4, "本年累计金额" == FY. For BS, "期末余额" for Q1 == 3-31 snapshot.

4. **Negative numbers**: Some Kingdee exports use Chinese 全角 minus `−` instead of `-`. Normalize to ASCII `-` before parsing.

5. **Trailing whitespace**: Account names sometimes have trailing `\u3000` (full-width space). Always `.strip()` after extracting.

6. **金额单位**: Kingdee default is 元 (yuan). If the report says 万元, divide by 10000 before writing to sheet. Don't mix units.

## Validation rules (must pass before using as formula source)

After writing 12 raw sheets, read back and assert:

- `资产负债表-2025Q4!C14` (资产总计) == `资产负债表-2025Q4!C30` (所有者权益合计) + `资产负债表-2025Q4!C25` (负债合计) ± 1 yuan
- `现金流量表-2025Q4!D11` (OCF 累计) == `SUM(现金流量表-2025Q1!C11, 现金流量表-2025Q2!C11, 现金流量表-2025Q3!C11, 现金流量表-2025Q4!C11)` (Q1-Q4 sum matches Q4 cumulative)
- `利润表-2025Q4!D2` (Q4 收入) == `利润表-2025Q4!C2` (Q4 累计收入) for Q1 only (Q2/Q3/Q4 累计 != 本期)
- `现金流量表-2025Q4!C25` (Q4 期末现金) == `资产负债表-2025Q4!C2` (Q4 货币资金) (CF 期末 vs BS 货币资金 must tie)
