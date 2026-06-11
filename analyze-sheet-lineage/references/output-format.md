# Spreadsheet Lineage Output Format

Use this structure for the final answer. The default presentation should be friendly Markdown that renders well in chat UIs and spreadsheets.

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

## 3. Tree Views Before The Table

Before the table, output tree structure first.

### 3.1 Simple Tree

Always include one short tree using `|__` style.

Example:

```md
依赖树：

ERP!BO2 主货号 = YSD028
|__ ERP!BN2 主货号辅助 = YSD028
   |__ ERP!B2 线上单号 = 260506M8EXBG1U
   |   |__ 订单!B117 Order ID = 260506M8EXBG1U
   |__ ERP!AB2 出库SKU = YSD030W40L60XY
   |   |__ 订单!P117 SKU Reference No. = YSD030W40L60XY
   |__ 订单!N117 Parent SKU Reference No. = YSD028
   |__ ERP!AE2 出库SPU = YSD030
```

### 3.2 Detailed Tree

When the chain contains lookup keys, matched rows, fallback branches, or other important details, include a second tree.

Example:

```md
详细依赖树：

ERP!BO2 主货号 = YSD028
|__ ERP!BN2 主货号辅助 = YSD028
   |__ 查找条件 1: ERP!B2 线上单号 = 260506M8EXBG1U
   |   |__ 匹配到: 订单!B117 Order ID = 260506M8EXBG1U
   |__ 查找条件 2: ERP!AB2 出库SKU = YSD030W40L60XY
   |   |__ 匹配到: 订单!P117 SKU Reference No. = YSD030W40L60XY
   |__ 返回字段: 订单!N117 Parent SKU Reference No. = YSD028
   |__ 备用回退: ERP!AE2 出库SPU = YSD030
   |__ 仅当 INDEX/MATCH 查找失败时使用；本次未使用
```

Rules:

- The simple tree is the default and should always appear.
- The simple tree must keep real structure depth. It may be shorter than the detailed tree, but it must not flatten nested relationships into one level.
- The detailed tree is recommended when it adds real explanatory value.
- Keep tree lines short enough to read in chat.

## 4. Main Table

After the tree block, output one detailed table.

The table should use dynamic layer columns. The number of `L` columns depends on actual lineage depth.

Examples:

- shallow chain: `L1 | L2 | 单元格 | 字段 | 值 | 作用说明`
- deeper chain: `L1 | L2 | L3 | L4 | 单元格 | 字段 | 值 | 作用说明`

Recommended default suffix columns:

| 单元格 | 字段 | 值 | 作用说明 |
| --- | --- | --- | --- |

Layer rules:

- `L1...Ln` only show structure.
- Put the node only in the column that corresponds to its layer.
- Leave the other layer columns empty.
- Use branch markers like `└─` or `├─` inside the `L` columns when helpful.
- If the chain depth is 2, use only `L1 | L2`.
- If the chain depth is 4, use `L1 | L2 | L3 | L4`.

Preferred full example:

| L1 | L2 | L3 | L4 | 单元格 | 字段 | 值 | 作用说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ERP!BO2 |  |  |  | ERP!BO2 | 主货号 | YSD028 | 目标单元格，最终输出 |
|  | └─ ERP!BN2 |  |  | ERP!BN2 | 主货号辅助 | YSD028 | BO2 的直接上游 |
|  |  | ├─ ERP!B2 |  | ERP!B2 | 线上单号 | 260506M8EXBG1U | BN2 的查找条件 1，用于匹配订单表 Order ID |
|  |  |  | └─ 订单!B117 | 订单!B117 | Order ID | 260506M8EXBG1U | 与 ERP!B2 匹配的订单号 |
|  |  | ├─ ERP!AB2 |  | ERP!AB2 | 出库SKU | YSD030W40L60XY | BN2 的查找条件 2，用于匹配订单表 SKU Reference No. |
|  |  |  | └─ 订单!P117 | 订单!P117 | SKU Reference No. | YSD030W40L60XY | 与 ERP!AB2 匹配的 SKU |
|  |  | ├─ 订单!N117 |  | 订单!N117 | Parent SKU Reference No. | YSD028 | BN2 实际取回的来源值 |
|  |  | └─ ERP!AE2 |  | ERP!AE2 | 出库SPU | YSD030 | BN2 查找失败时的备用回退，本次未使用 |

Rules:

- The `L` columns express the graph shape.
- `单元格 | 字段 | 值 | 作用说明` express readable details.
- Do not put long formulas into this main table by default.

## 5. Calculation Steps

After the table, add a short `计算过程：` section with 3 to 6 numbered steps.

Example:

```md
计算过程：

1. ERP!BN2 先用 ERP!B2 的订单号和 ERP!AB2 的出库 SKU 去“订单”表查找。
2. 匹配条件命中“订单”表第 117 行。
3. BN2 返回订单!N117 的 Parent SKU Reference No.，得到 YSD028。
4. ERP!BO2 再对 BN2 做清洗；当前 BN2 不包含 `-`，所以最终回退为 BN2 本身。
```

## 6. Formulas

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

依赖树：

ERP!BO2 主货号 = YSD028
|__ ERP!BN2 主货号辅助 = YSD028
   |__ ERP!B2 线上单号 = 260506M8EXBG1U
   |   |__ 订单!B117 Order ID = 260506M8EXBG1U
   |__ ERP!AB2 出库SKU = YSD030W40L60XY
   |   |__ 订单!P117 SKU Reference No. = YSD030W40L60XY
   |__ 订单!N117 Parent SKU Reference No. = YSD028
   |__ ERP!AE2 出库SPU = YSD030

详细依赖树：

ERP!BO2 主货号 = YSD028
|__ ERP!BN2 主货号辅助 = YSD028
   |__ 查找条件 1: ERP!B2 线上单号 = 260506M8EXBG1U
   |   |__ 匹配到: 订单!B117 Order ID = 260506M8EXBG1U
   |__ 查找条件 2: ERP!AB2 出库SKU = YSD030W40L60XY
   |   |__ 匹配到: 订单!P117 SKU Reference No. = YSD030W40L60XY
   |__ 返回字段: 订单!N117 Parent SKU Reference No. = YSD028
   |__ 备用回退: ERP!AE2 出库SPU = YSD030

| L1 | L2 | L3 | L4 | 单元格 | 字段 | 值 | 作用说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ERP!BO2 |  |  |  | ERP!BO2 | 主货号 | YSD028 | 目标单元格，最终输出 |
|  | └─ ERP!BN2 |  |  | ERP!BN2 | 主货号辅助 | YSD028 | BO2 的直接上游 |
|  |  | ├─ ERP!B2 |  | ERP!B2 | 线上单号 | 260506M8EXBG1U | BN2 的查找条件 1，用于匹配订单表 Order ID |
|  |  |  | └─ 订单!B117 | 订单!B117 | Order ID | 260506M8EXBG1U | 与 ERP!B2 匹配的订单号 |
|  |  | ├─ ERP!AB2 |  | ERP!AB2 | 出库SKU | YSD030W40L60XY | BN2 的查找条件 2，用于匹配订单表 SKU Reference No. |
|  |  |  | └─ 订单!P117 | 订单!P117 | SKU Reference No. | YSD030W40L60XY | 与 ERP!AB2 匹配的 SKU |
|  |  | ├─ 订单!N117 |  | 订单!N117 | Parent SKU Reference No. | YSD028 | BN2 实际取回的来源值 |
|  |  | └─ ERP!AE2 |  | ERP!AE2 | 出库SPU | YSD030 | BN2 查找失败时的备用回退，本次未使用 |

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
