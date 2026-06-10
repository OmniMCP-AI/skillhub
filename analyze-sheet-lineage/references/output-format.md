# Spreadsheet Lineage Output Format

Use this structure for the final answer. The default presentation should be friendly Markdown that renders well in chat UIs.

## 1. Title

Use a short title like:

```md
### ERP!BO2 单元格血缘分析
```

## 2. Conclusion

Use one short paragraph or one sentence starting with `结论：`.

Good example:

```md
结论：ERP!BO2 的值 YSD028 来自 ERP!BN2；ERP!BN2 又通过订单号和出库 SKU，在“订单”表中匹配到第 117 行，并取回 Parent SKU Reference No.
```

Keep it short and business-readable.

## 3. Main Table

The default table should be concise and easy to render.

Recommended columns:

| 层级 | 单元格 | 字段 | 值 | 说明 |
| ---: | --- | --- | --- | --- |

Column rules:

- `层级`
  - Use simple depth labels such as `0`, `1`, `2`, `3`, or `备用`.
- `单元格`
  - Use direct addresses like `ERP!BO2`, `订单!N117`.
- `字段`
  - Prefer business-facing labels when available, such as `主货号`, `出库SKU`, `Order ID`.
  - If the field name is unknown, use `—`.
- `值`
  - Show the actual computed or literal value.
- `说明`
  - One short phrase describing the role of the row.

## 4. Calculation Steps

After the table, add a short `计算过程：` section with 3 to 6 numbered steps.

Example:

```md
计算过程：

1. ERP!BN2 先用 ERP!B2 的订单号和 ERP!AB2 的出库 SKU 去“订单”表查找。
2. 匹配条件命中“订单”表第 117 行。
3. BN2 返回订单!N117 的 Parent SKU Reference No.，得到 YSD028。
4. ERP!BO2 再对 BN2 做清洗；当前 BN2 不包含 `-`，所以最终回退为 BN2 本身。
```

## 5. Formulas

Put formulas after the explanation, not inside the main table by default.

Preferred format:

```md
公式：

ERP!BO2

```excel
=...
```

ERP!BN2

```excel
=...
```
```

Rules:

- Keep exact formulas for the target cell and the most important direct precedent.
- Lower-level formulas may be omitted if they are just literals or add little value.

## 6. Optional Tree View

Tree view is optional. Do not use it as the default main artifact.

Use only when:

- the user explicitly asks for a dependency tree
- the chain is easier to explain as a tree than as a table

If used, place it after the main table or after `计算过程`.

Valid example:

```md
依赖树：

ERP!BO2
|_ ERP!BN2
   |_ ERP!B2
   |_ ERP!AB2
   |_ 订单!N117
   |_ ERP!AE2
```

Do not embed this tree directly inside a Markdown table cell.

## 7. Optional Mermaid

Add Mermaid only when one of these is true:

- the user explicitly asks for a diagram
- the lineage has enough stable structure that a diagram helps more than it distracts

If Mermaid is omitted, do not apologize.

## 8. Uncertainty / Caveats

Add this section only when needed.

Recommended wording:

- `Certain:` facts directly read from formula text or sheet data
- `Uncertain:` inferred, unresolved, or engine-dependent parts

## Minimal Example

```md
### ERP!BO2 单元格血缘分析

结论：ERP!BO2 的值 YSD028 来自 ERP!BN2；ERP!BN2 又通过订单号和出库 SKU，在“订单”表中匹配到第 117 行，并取回 Parent SKU Reference No.

| 层级 | 单元格 | 字段 | 值 | 说明 |
| ---: | --- | --- | --- | --- |
| 0 | ERP!BO2 | 主货号 | YSD028 | 目标单元格，最终输出结果 |
| 1 | ERP!BN2 | 主货号辅助 | YSD028 | BO2 的直接上游 |
| 2 | ERP!B2 | 线上单号 | 260506M8EXBG1U | 用于匹配“订单”表的 Order ID |
| 2 | ERP!AB2 | 出库SKU | YSD030W40L60XY | 用于匹配“订单”表的 SKU Reference No. |
| 3 | 订单!B117 | Order ID | 260506M8EXBG1U | 命中的订单号 |
| 3 | 订单!P117 | SKU Reference No. | YSD030W40L60XY | 命中的 SKU |
| 3 | 订单!N117 | Parent SKU Reference No. | YSD028 | BN2 实际取回的来源值 |
| 备用 | ERP!AE2 | — | YSD030 | 仅当 BN2 查找失败时回退使用 |

计算过程：

1. ERP!BN2 先用 ERP!B2 的订单号和 ERP!AB2 的出库 SKU 去“订单”表查找。
2. 匹配条件命中“订单”表第 117 行。
3. BN2 返回订单!N117 的 Parent SKU Reference No.，得到 YSD028。
4. ERP!BO2 再对 BN2 做清洗；当前 BN2 不包含 `-`，所以最终回退为 BN2 本身。

公式：

ERP!BO2

```excel
=IFERROR(IF(OR(ISNUMBER(SEARCH({"TEST","测品"},BN2))),BN2,LEFT(BN2,FIND("-",BN2)-1)),BN2)
```

ERP!BN2

```excel
=IFERROR(INDEX(订单!N:N,MATCH(1,(订单!B:B=B2)*ISNUMBER(FIND(AB2,订单!P:P)),0)),AE2)
```
```
