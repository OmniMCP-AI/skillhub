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
- one friendly Markdown table as the primary presentation
- direct precedents
- recursive dependency chain when needed
- concise explanation in Chinese
- Mermaid diagram only as optional supplement
- caveats / uncertainty notes when needed

Preferred default answer structure:

- title
- `结论：...`
- one Markdown table
- `计算过程：`
- formula code blocks

Preferred default table columns:

- `层级`
- `单元格`
- `字段`
- `value`
- `说明`

Important rendering rules:

1. Do not put long formulas into the main table by default.
2. Do not put ASCII tree markers like `|_` into the main table by default.
3. Put formulas into fenced `excel` blocks after the explanation.
4. Tree view is optional and should be separate from the main table.
