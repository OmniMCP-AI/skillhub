# Spreadsheet Lineage Read Workflow

## Scope

Phase 2 only explains how to read lineage from existing sheet data. It does not introduce a new backend lineage API.

Shared contract:

- Resolve the target from `selected_range` first.
- Use `spreadsheet_url` to identify the document and worksheet context.
- Read formulas with `read_sheet(value_render_option="FORMULA")`.
- Read the minimum range needed.

## 1. Target Resolution

1. Parse `selected_range`.
2. If it is a single cell, treat that cell as the target.
3. If it is a range, treat the whole range as the target and analyze each populated/formula cell inside it.
4. Use `spreadsheet_url` and `gid` only to confirm workbook and sheet context. Do not override `selected_range`.

## 2. Read Order

Recommended call order:

1. Read the target cell or target range with `read_sheet(..., value_render_option="FORMULA")`.
2. Inspect returned formulas or literals.
3. Parse direct A1 references from each target formula.
4. For every precedent not yet resolved, read only that referenced cell or range with `read_sheet(..., value_render_option="FORMULA")`.
5. Repeat recursively until a stop condition is reached.

Minimal principle:

- Single cell target: read one cell first.
- Range target: read only the selected rectangle first.
- Precedent expansion: read referenced addresses only, not the whole sheet.

## 3. Direct Precedents

Direct precedents are the cells or ranges explicitly referenced by the target formula.

Examples:

- `=A1+B1` -> direct precedents: `A1`, `B1`
- `=Sheet2!C3` -> direct precedent: `Sheet2!C3`
- `=SUM(B2:B5)` -> direct precedent range: `B2:B5`

Phase 2 should report what is directly visible from the formula text, not inferred hidden dependencies.

## 4. Recursive Rule

Recursive expansion applies only when a direct precedent cell itself contains a formula.

Rule:

1. Read the precedent with `FORMULA`.
2. If the returned value is a formula, parse its direct precedents.
3. Append them to the dependency chain.
4. Continue depth-first or breadth-first; either is acceptable if the output is stable and clear.
5. De-duplicate already visited addresses to avoid loops and repeated reads.

## 5. Stop Conditions

Stop recursion when any of these is true:

- The current cell is a literal value, not a formula.
- The reference is empty or unresolved.
- The address has already been visited.
- The dependency chain becomes too deep to trust confidently.
- The formula uses unsupported or ambiguous constructs.

When stopping early, return the partial lineage and mark it as incomplete.

## 6. Uncertainty Handling

Explicitly mark uncertainty for:

- named ranges
- spill / array formulas
- SQL formulas
- indirect references such as `INDIRECT`
- dynamic address builders such as `ADDRESS`, `OFFSET`
- ambiguous mixed-engine results
- very deep chains where cost or confidence becomes poor

Preferred behavior:

- Keep confirmed direct precedents.
- Label uncertain nodes as `unresolved` or `engine-dependent`.
- Do not over-claim recursive lineage beyond what `FORMULA` text clearly supports.

## 7. Excelize / PG Difference Reminder

Phase 2 reads lineage from formula text, but execution engines may still differ.

Remind the caller:

- Excelize and PG may evaluate the same workbook differently.
- Spill behavior, function support, and range expansion may not match.
- A formula readable from `FORMULA` text is not proof that both engines compute identical dependencies.
- If lineage depends on engine-specific behavior, mark the result as a caveat instead of forcing one interpretation.

## 8. Expected Output Shape

The workflow should try to produce:

- target cell or target range
- title
- concise conclusion
- one simple tree block
- one detailed tree block when useful
- one Markdown table as the primary artifact
- short calculation steps
- formula code blocks for the target and key direct precedents
- direct precedents
- recursive dependency chain
- caveats for uncertainty
- Mermaid diagram only when explicitly useful

## 9. Friendly Markdown Rule

Optimize for chat rendering first.

1. Put one simple `|__` tree before the main table.
2. Add one detailed `|__` tree when lookup keys, matched rows, or fallback branches matter.
3. Keep the main table simple and spreadsheet-friendly.
4. Do not place long formulas inside the main table by default.
5. Move long formulas into fenced `excel` code blocks after the explanation.
6. Use business-readable field names whenever possible.

## 10. Main Table Construction Rule

After resolving lineage, normalize the final answer into rows.

Recommended row strategy:

1. Row `1` is always the target cell or range.
2. The next rows contain direct precedents of the target formula.
3. Deeper rows contain recursive supports such as lookup keys, matched source cells, fallback literals, or deeper precedent formulas.
4. Keep the number of rows small. Prefer 4 to 10 high-signal rows over exhaustive dumps.
5. The shape should remain readable after copy/paste into chat or spreadsheets.

Recommended default columns:

- `L1 ... Ln`
- `单元格`
- `字段`
- `值`
- `作用说明`

Layer column rules:

1. Use dynamic layer columns such as `L1 | L2` or `L1 | L2 | L3 | L4`.
2. Put each node only in the column for its actual depth.
3. Leave other layer columns blank.
4. Use markers like `└─` or `├─` inside the `L` columns when they improve readability.
5. Do not force `L4` when only two or three layers exist.

## 11. Optional Tree Structure Rule

The tree view should be separate from the main table and should come before the table.

Recommended branch labels:

- `Sheet1!F8`
- `|__ Orders!C8`
- `   |__ ERP!B2`
- `   |__ 订单!N117`
- `   |__ ERP!AE2`

ASCII-only tree style is also allowed when that is easier to copy into spreadsheets or plain-text environments:

- `Sheet1!F8`
- `|__ Orders!C8`
- `   |__ ERP!B2`
- `   |__ 订单!N117`

Rules:

1. Put the most important identity first: cell or range address.
2. Use branch markers only to communicate structure, not decoration.
3. The simple tree should always appear.
4. Add a detailed tree when it materially improves understanding.
5. Do not try to render the entire graph with ASCII art.
6. Do not embed the full tree inside the main Markdown table by default.

## 12. Formula Display Rule

Formula display should balance fidelity and readability.

1. Keep the exact target formula whenever possible.
2. Keep exact direct-precedent formulas when they are central to the explanation.
3. Lower-level rows may use `literal` or short summaries if the exact formula adds little value.
4. Do not repeat the same long formula in multiple rows unless it helps the reader.
5. Prefer separate formula blocks after the main table:
   - target formula
   - key direct-precedent formula
6. Only keep formulas inside the main table when the user explicitly asks for a technical matrix view.

## 13. Explanation Rule

The `作用说明` column should explain role, not restate the formula.

Good examples:

- `target output`
- `direct precedent`
- `MATCH key`
- `matched return value`
- `fallback value`
- `downstream consumer`

Avoid long prose in the table. Keep each explanation as one short phrase.

## 14. Calculation Steps Rule

After the main table, add `计算过程：` with 3 to 6 short numbered steps.

The steps should:

1. Explain matching or lookup logic first.
2. Explain the returned source value second.
3. Explain any cleanup or transformation logic last.
4. Prefer business-readable wording over formula-token restatement.
