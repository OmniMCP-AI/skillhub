# Spreadsheet Lineage Read Workflow

## Scope

Phase 2 only explains how to read lineage from existing sheet data. It does not introduce a new backend lineage API.

Shared contract:

- Resolve the target from `selected_range` first.
- Use `spreadsheet_url` to identify the document and worksheet context.
- Read formulas with `read_sheet(value_render_option="FORMULA")`.
- Read the minimum range needed.
- When available, read write-time sidecar metadata by `doc_id + gid + cell/range` as supplemental provenance.
- Do not create helper worksheets, source-tracking worksheets, confidence mirrors, or workbook style changes during lineage analysis.

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
6. If sidecar metadata exists, query it only for the target cells and confirmed lineage cells.

Minimal principle:

- Single cell target: read one cell first.
- Range target: read only the selected rectangle first.
- Precedent expansion: read referenced addresses only, not the whole sheet.
- Sidecar metadata lookup: query the smallest cell/range set needed, not the whole workbook.

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
- sidecar metadata whose `value_hash` no longer matches the current visible value

Preferred behavior:

- Keep confirmed direct precedents.
- Label uncertain nodes as `unresolved` or `engine-dependent`.
- Do not over-claim recursive lineage beyond what `FORMULA` text clearly supports.
- Do not over-claim sidecar metadata as formula lineage. It is provenance or confidence context only.

## 6A. Sidecar Metadata Usage

Use sidecar metadata when the caller asks where a literal or generated value came from, or when formula lineage reaches a literal cell with source metadata.

Supported behavior:

1. Parse `doc_id` and `gid` from `spreadsheet_url` or caller context.
2. Query play-be cell metadata for the selected cell/range and confirmed lineage cells.
3. Match records by `doc_id`, `gid`, and A1 `cell`; use `row` and `col` to validate coordinates.
4. Compare current visible value hash with `value_hash` when possible.
5. Label sidecar facts as `来源元数据` or `置信度元数据`, not as formula precedents.
6. If metadata is stale, show it as a caveat and do not use it as proof of the current value.
7. If `source_refs` is empty, state that no stable source reference was recorded.
8. Keep `confidence_level` as numeric `1-5`; do not convert it into a color or style action.

Lineage analysis is read-only. If sidecar metadata is missing, do not create it; direct the caller to `track-sheet-sources` or `assess-sheet-confidence`.

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
- one simple DAG block as the default artifact
- one optional tree block when useful
- one Markdown table only in deep explain mode
- short calculation steps
- formula code blocks for the target and key direct precedents
- direct precedents
- recursive dependency chain
- sidecar source/confidence facts when available
- caveats for uncertainty
- Mermaid diagram only when explicitly useful

## 9. Friendly Markdown Rule

Optimize for chat rendering first.

1. Put one simple ASCII DAG after the conclusion by default.
2. Use the DAG to show the main path with short action labels between nodes.
3. Add one `|__` tree only when branching structure needs extra clarification or the user explicitly asks for tree format.
4. Keep the main table for deep explain mode instead of the default answer.
5. Do not place long formulas inside the main table by default.
6. Move long formulas into fenced `excel` code blocks after the explanation.
7. Use business-readable field names whenever possible.
8. If a tree is included, it still needs true depth. If one lookup key resolves to a matched row, the matched row should be nested under that key, not shown as a flat sibling.

## 10. Main Table Construction Rule

After resolving lineage, normalize the final answer into rows.

This rule applies when deep explain mode needs a table. It is not mandatory for the default lightweight answer.

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
- `公式`
- `值`
- `作用说明`

Layer column rules:

1. Use dynamic layer columns such as `L1 | L2` or `L1 | L2 | L3 | L4`.
2. Put each node only in the column for its actual depth.
3. Leave other layer columns blank.
4. Use markers like `└─` or `├─` inside the `L` columns when they improve readability.
5. Do not force `L4` when only two or three layers exist.
6. Keep one `公式` column in the main table.
7. Use `literal` for non-formula rows.
8. For long formulas, keep a compact readable formula string in the table and retain the full exact formula in later fenced `excel` blocks.

## 11. Optional Tree Structure Rule

The tree view is optional and should be separate from the main table.

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
3. The simple tree should appear only when it adds value or the user asks for it.
4. The simple tree must preserve real parent-child depth, even when it omits some labels or notes.
5. Add a detailed tree when it materially improves understanding.
6. Do not try to render the entire graph with ASCII art if the default DAG already explains the main path clearly.
7. Do not embed the full tree inside the main Markdown table by default.

## 11A. Default DAG Rule

The default lightweight view should be a simple DAG-like ASCII flow.

Rules:

1. Start from the most relevant source node or matched source row.
2. Flow toward the target cell, or continue forward to the downstream consumer when that helps answer the question better.
3. Use boxed nodes with 1 to 3 key lines inside each box.
4. Put short action labels on the arrows.
5. Prefer one main chain over a fully exhaustive graph.
6. When the graph branches too much, keep the DAG focused and mention side branches separately or switch to tree/table mode.

## 12. Formula Display Rule

Formula display should balance fidelity and readability.

1. Keep the exact target formula whenever possible.
2. Keep exact direct-precedent formulas when they are central to the explanation.
3. Lower-level rows may use `literal` or short summaries if the exact formula adds little value.
4. Do not repeat the same long formula in multiple rows unless it helps the reader.
5. Prefer separate formula blocks after the main table:
   - target formula
   - key direct-precedent formula
6. Even when formula blocks are present, keep one short `公式` column in the table so each layer has an immediate formula or `literal`.

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
