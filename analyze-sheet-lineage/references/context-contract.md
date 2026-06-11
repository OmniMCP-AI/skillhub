# Spreadsheet Lineage Context Contract

## Input tags

The skill and workflow assume the caller may provide:

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`
- `[current_url=...]`
- `[selected_range=Sheet1!B3]` or `[selected_range=Sheet1!B3:D10]`

`selected_range` is the primary target selector. For a single cell, it is the active cell.

## Required behavior

1. Use `selected_range` first to determine the target cell or range.
2. Use `spreadsheet_url` to resolve the document and current worksheet context.
3. Use existing spreadsheet read capabilities, not a new backend lineage API.
4. Read formulas with `read_sheet` and `value_render_option = "FORMULA"`.
5. Read only the minimum required range whenever possible.

## Workflow boundary

This skill is optimized for:

- normal A1 references
- cross-worksheet references
- direct precedents
- recursive precedents

This skill should explicitly mark uncertainty for:

- named ranges
- spill / array formulas
- SQL formulas
- very deep or ambiguous dependency chains
- cases where engine-specific behavior differs between Excelize and PG

## Output minimum

The final answer should try to include:

- target cell or target range
- one friendly Markdown tree block
- one friendly Markdown table as the primary detailed presentation
- direct precedents
- recursive dependency chain when needed
- concise explanation in Chinese
- Mermaid diagram only as optional supplement
- caveats / uncertainty notes when needed

Preferred default answer structure:

- title
- `结论：...`
- `依赖树：`
- `详细依赖树：` when useful
- one Markdown table with dynamic `L1...Ln` layer columns
- `计算过程：`
- formula code blocks

Preferred default table columns:

- `L1 ... Ln`
- `单元格`
- `字段`
- `值`
- `说明`

Important rendering rules:

1. Do not put long formulas into the main table by default.
2. Do not put the full ASCII tree text into the main table cells by default.
3. Use `|__` tree blocks before the table, not instead of the table.
4. Put formulas into fenced `excel` blocks after the explanation.
5. The number of layer columns should match actual depth. Use `L1 | L2` for shallow chains and expand only when needed.
