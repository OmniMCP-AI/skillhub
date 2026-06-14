# Spreadsheet Lineage Verification

## Goal

Verify that the workflow can read formula-based lineage correctly with `read_sheet(value_render_option="FORMULA")`, and can present the result in a friendly Markdown format that renders well in chat, with a simple DAG as the default artifact, tree as optional, and a layered table only in deep explain mode.

When write-time sidecar metadata is available, also verify that lineage can display source/confidence metadata without treating it as a formula precedent.

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
- output includes a short conclusion, a simple DAG, calculation steps, and formula blocks
- optional tree and deep-explain table appear only when requested or clearly helpful

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
- DAG, optional tree, and deep-explain table stay readable and do not dump the whole range blindly

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
- the default DAG remains readable after crossing worksheets; tree/table only appear when needed

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
3. There is one simple DAG-like block by default.
4. There is one simple `依赖树：` block using `|__` only when tree format is useful.
5. There is one `详细依赖树：` block only when lookup or fallback details matter.
6. There is one Markdown table only in deep explain mode.
7. When present, the deep explain table columns are business-readable and layer-aware:
   - `L1 ... Ln`
   - `单元格`
   - `字段`
   - `公式`
   - `值`
   - `作用说明`
8. There is one short `计算过程：` section.
9. There are fenced `excel` blocks for the target formula and key direct-precedent formula.
10. Mermaid is absent unless the user explicitly asked for it or the table is insufficient.
11. The full ASCII tree is not stuffed into the main table cells.
12. If a tree is present, the simple tree preserves actual depth instead of flattening nested matched rows into sibling lines.
13. The default DAG is wrapped in one fenced `text` code block.
14. Box borders stay aligned and values do not spill outside the right frame.

## 5A. Sidecar Metadata Review

Check a target range that has play-be sidecar metadata.

Steps:

1. Query metadata by `doc_id + gid + cell/range`.
2. Confirm sidecar rows match requested cells or confirmed lineage cells.
3. Confirm header row 1 and column A are absent when default product skip rules applied during write-time metadata generation.
4. Confirm each metadata row has `doc_id`, `gid`, `cell`, `row`, `col`, and `value_hash`.
5. Confirm `source_refs` are real recorded evidence and are not invented during lineage analysis.
6. Confirm every present `confidence_level` is numeric `1` through `5`.
7. Compare visible values against `value_hash` when possible and mark stale metadata clearly.

Pass criteria:

- sidecar facts appear as source/confidence metadata, not direct formula precedents
- missing metadata is reported as missing, not regenerated
- stale metadata is caveated
- no worksheet, helper cell, or style change is made

## 6. Reference Example: ERP!BO2

Use this as a smoke test example when possible.

Expected default shape:

主链路：

```text
订单表
┌──────────────────────────────┐
│ B117 订单号: 260506M8EXBG1U  │
│ P117 SKU: YSD030W40L60XY     │
│ N117 主货号: YSD028          │
└──────────────┬───────────────┘
               │
               │ 匹配订单号 + SKU
               ▼
ERP!BN2
┌──────────────────────────────┐
│ 值: YSD028                   │
└──────────────┬───────────────┘
               │
               │ 清洗货号格式
               ▼
ERP!BO2
┌──────────────────────────────┐
│ 值: YSD028                   │
└──────────────────────────────┘
```

Expected optional tree:

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

Expected deep explain table:

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

- the DAG shows the main path clearly without Mermaid
- `ERP!BN2` appears as the key intermediate node between source and target
- if the optional tree is used, it nests `订单!B117` under `ERP!B2`, and nests `订单!P117` under `ERP!AB2`
- if the deep explain table is used, it includes a `公式` column for every row, using formula text or `literal`
- source keys and matched source values are visible without reading raw formulas first
- the output is understandable without Mermaid
- the output looks correct as rendered Markdown, not just as plain text
- the box frame remains intact in rendered chat screenshots, with no right-border spill

## 7. Minimal Review Checklist

- Target came from `selected_range`
- Workbook/sheet context came from `spreadsheet_url`
- Reads used `value_render_option="FORMULA"`
- Read scope stayed minimal
- Output distinguishes `direct precedents` from recursive lineage
- Output uses simple DAG Markdown as the default artifact
- Tree is optional
- Layered table is reserved for deep explain mode
- Output includes caveats for uncertain or engine-dependent cases
