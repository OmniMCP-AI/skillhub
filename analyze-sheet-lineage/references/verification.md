# Spreadsheet Lineage Verification

## Goal

Verify that the workflow can read formula-based lineage correctly with `read_sheet(value_render_option="FORMULA")`, and can present the result in a friendly Markdown format that renders well in chat, with tree blocks plus a layered table.

## 1. Single Cell

Check one target such as `Sheet1!C3`.

Steps:

1. Read `Sheet1!C3` with `FORMULA`.
2. Confirm the raw formula text matches the sheet.
3. Extract direct precedents from the formula.
4. Read each precedent cell with `FORMULA`.
5. Confirm literals stop recursion and formulas continue recursion.

Pass criteria:

- target cell is correct
- direct precedents match visible formula references
- recursive chain stops at literals or declared stop conditions
- output includes a short conclusion, a simple tree, a concise layered Markdown table, calculation steps, and formula blocks

## 2. Multi-Cell Range

Check a target such as `Sheet1!C3:E6`.

Steps:

1. Read only `C3:E6` with `FORMULA`.
2. Identify which cells in the range are formulas versus literals.
3. Build lineage per formula cell.
4. Merge repeated precedents without losing per-cell attribution.

Pass criteria:

- range scope is preserved
- each formula cell has its own direct precedents
- shared upstream cells are de-duplicated in the recursive graph
- tree and table stay readable and do not dump the whole range blindly

## 3. Cross-Sheet References

Check formulas like `=Sheet2!B4` or `=SUM(Sheet2!B2:B5)`.

Steps:

1. Read the source formula cell on the current sheet.
2. Confirm cross-sheet tokens are parsed with sheet names intact.
3. Read the referenced cells or ranges from the other sheet with `FORMULA`.
4. Continue recursion only from the referenced cells that are formulas.

Pass criteria:

- sheet names are preserved exactly
- lineage crosses worksheets correctly
- no implicit sheet rewrite happens during parsing
- the tree plus main Markdown table still stay readable after crossing worksheets

## 4. Boundary Cases

Validate and label these cases explicitly:

- named ranges
- spill / array formulas
- `INDIRECT`, `OFFSET`, `ADDRESS`
- empty cells
- broken references such as `#REF!`
- circular or repeated references
- very deep dependency chains
- formulas whose engine behavior may differ between Excelize and PG

Pass criteria:

- confirmed references are still reported
- unresolved parts are marked clearly
- recursion stops safely on loops, broken refs, or low-confidence cases
- output includes an engine-difference caveat where needed
- the table does not over-claim structure when the graph is ambiguous

## 5. Output Shape Review

Check the answer shape directly.

Required checks:

1. There is one short title.
2. There is one short `结论：` paragraph.
3. There is one simple `依赖树：` block using `|__`.
4. There is one `详细依赖树：` block when lookup or fallback details matter.
5. There is one Markdown table.
6. The default table columns are business-readable and layer-aware:
   - `L1 ... Ln`
   - `单元格`
   - `字段`
   - `公式`
   - `值`
   - `作用说明`
7. There is one short `计算过程：` section.
8. There are fenced `excel` blocks for the target formula and key direct-precedent formula.
9. Mermaid is absent unless the user explicitly asked for it or the table is insufficient.
10. The full ASCII tree is not stuffed into the main table cells.
11. The simple tree preserves actual depth instead of flattening nested matched rows into sibling lines.

## 6. Reference Example: ERP!BO2

Use this as a smoke test example when possible.

Expected shape:

依赖树：

```text
ERP!BO2 主货号 = YSD028
|__ ERP!BN2 主货号辅助 = YSD028
   |__ ERP!B2 线上单号 = 260506M8EXBG1U
   |   |__ 订单!B117 Order ID = 260506M8EXBG1U
   |__ ERP!AB2 出库SKU = YSD030W40L60XY
   |   |__ 订单!P117 SKU Reference No. = YSD030W40L60XY
   |__ 订单!N117 Parent SKU Reference No. = YSD028
   |__ ERP!AE2 出库SPU = YSD030
```

| L1 | L2 | L3 | L4 | 单元格 | 字段 | 公式 | 值 | 作用说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ERP!BO2` |  |  |  | `ERP!BO2` | `主货号` | `=IFERROR(IF(...),BN2)` | `YSD028` | `目标单元格，最终输出` |
|  | `└─ ERP!BN2` |  |  | `ERP!BN2` | `主货号辅助` | `=IFERROR(INDEX(...),AE2)` | `YSD028` | `BO2 的直接上游` |
|  |  | `├─ ERP!B2` |  | `ERP!B2` | `线上单号` | `literal` | `260506M8EXBG1U` | `BN2 的查找条件 1` |
|  |  |  | `└─ 订单!B117` | `订单!B117` | `Order ID` | `literal` | `260506M8EXBG1U` | `与 ERP!B2 匹配的订单号` |
|  |  | `├─ ERP!AB2` |  | `ERP!AB2` | `出库SKU` | `literal` | `YSD030W40L60XY` | `BN2 的查找条件 2` |
|  |  |  | `└─ 订单!P117` | `订单!P117` | `SKU Reference No.` | `literal` | `YSD030W40L60XY` | `与 ERP!AB2 匹配的 SKU` |
|  |  | `├─ 订单!N117` |  | `订单!N117` | `Parent SKU Reference No.` | `literal` | `YSD028` | `BN2 实际取回的来源值` |
|  |  | `└─ ERP!AE2` |  | `ERP!AE2` | `出库SPU` | `literal` | `YSD030` | `BN2 查找失败时的备用回退，本次未使用` |

Pass criteria:

- `ERP!BO2` appears in the first row and first layer column
- `ERP!BN2` appears as the direct child row
- the simple tree nests `订单!B117` under `ERP!B2`, and nests `订单!P117` under `ERP!AB2`
- the main table includes a `公式` column for every row, using formula text or `literal`
- source keys and matched source values are visible without reading raw formulas first
- the output is understandable without Mermaid
- the output looks correct as rendered Markdown, not just as plain text

## 7. Minimal Review Checklist

- Target came from `selected_range`
- Workbook/sheet context came from `spreadsheet_url`
- Reads used `value_render_option="FORMULA"`
- Read scope stayed minimal
- Output distinguishes `direct precedents` from recursive lineage
- Output uses tree plus layered-table Markdown as the default artifact
- Output includes caveats for uncertain or engine-dependent cases
