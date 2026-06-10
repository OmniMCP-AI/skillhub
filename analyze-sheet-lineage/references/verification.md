# Spreadsheet Lineage Verification

## Goal

Verify that the workflow can read formula-based lineage correctly with `read_sheet(value_render_option="FORMULA")`, and can present the result in a friendly Markdown format that renders well in chat.

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
- output includes a short conclusion, a concise Markdown table, calculation steps, and formula blocks

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
- table rows stay readable and do not dump the whole range blindly

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
- the main Markdown table still stays readable after crossing worksheets

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
3. There is one Markdown table.
4. The default table columns are business-readable:
   - `层级`
   - `单元格`
   - `字段`
   - `值`
   - `说明`
5. There is one short `计算过程：` section.
6. There are fenced `excel` blocks for the target formula and key direct-precedent formula.
7. Mermaid is absent unless the user explicitly asked for it or the table is insufficient.
8. Raw tree glyphs are not embedded inside the default main table.

## 6. Reference Example: ERP!BO2

Use this as a smoke test example when possible.

Expected shape:

| 层级 | 单元格 | 字段 | 值 | 说明 |
| ---: | --- | --- | --- | --- |
| 0 | `ERP!BO2` | `主货号` | `YSD028` | `目标单元格，最终输出结果` |
| 1 | `ERP!BN2` | `主货号辅助` | `YSD028` | `BO2 的直接上游` |
| 2 | `ERP!B2` | `线上单号` | `260506M8EXBG1U` | `用于匹配订单表的 Order ID` |
| 2 | `ERP!AB2` | `出库SKU` | `YSD030W40L60XY` | `用于匹配订单表的 SKU Reference No.` |
| 3 | `订单!B117` | `Order ID` | `260506M8EXBG1U` | `命中的订单号` |
| 3 | `订单!P117` | `SKU Reference No.` | `YSD030W40L60XY` | `命中的 SKU` |
| 3 | `订单!N117` | `Parent SKU Reference No.` | `YSD028` | `BN2 实际取回的来源值` |
| 备用 | `ERP!AE2` | `—` | `YSD030` | `仅当 BN2 查找失败时回退使用` |

Pass criteria:

- `ERP!BO2` is row `0`
- `ERP!BN2` is row `1`
- source keys and matched source values are visible without reading raw formulas first
- the output is understandable without Mermaid
- the output looks correct as rendered Markdown, not just as plain text

## 7. Minimal Review Checklist

- Target came from `selected_range`
- Workbook/sheet context came from `spreadsheet_url`
- Reads used `value_render_option="FORMULA"`
- Read scope stayed minimal
- Output distinguishes `direct precedents` from recursive lineage
- Output uses friendly Markdown as the default artifact
- Output includes caveats for uncertain or engine-dependent cases
