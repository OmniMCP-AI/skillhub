---
name: analyze-sheet-lineage
description: Explains spreadsheet cell lineage, precedents, and dependency chains from a selected cell or range. Use when the user asks why a value appears, where a formula pulls from, what cells depend on what, or wants a dependency chain table for a workbook cell/range.
---

# Analyze Sheet Lineage

Use this skill for explanation-layer lineage work, not for building a new backend lineage API.

Shared contract: read `context-contract.md` first. It defines the input tags, the preferred selectors, the workflow boundary, and the minimum output.

## Trigger

Trigger when the user asks any of these:

- why a cell has its value
- which cells a formula depends on
- upstream / downstream / precedent / dependent / lineage / dependency chain
- cross-sheet formula tracing
- "draw the relationship" for a selected cell or range

Strong hints include terms like `血缘`, `依赖链`, `前置单元格`, `来源`, `trace`, `precedent`, `dependency`, `lineage`, `Mermaid`.

Do not use this skill for pure calculation help, formatting, or business interpretation with no dependency-tracing intent.

## How To Decide

1. Use `selected_range` as the primary target.
2. If the user names a cell/range explicitly, treat that as the target even if wording is informal.
3. If the request asks "why", "from where", or "depends on what", treat it as lineage analysis.
4. If the request is ambiguous between value interpretation and lineage, answer the lineage part and state the uncertainty.

## What To Read

- Always read `context-contract.md`.
- Read `output-format.md` before producing the final answer.
- Read `lineage-json-schema.md` when you need a normalized internal lineage object for reasoning or multi-step tracing.
- Read `workflow.md` only when present and when the task needs step-by-step execution guidance beyond the shared contract, such as recursive tracing strategy, formula parsing order, or range-expansion rules.

## Output Rules

- The default output is friendly Markdown for chat rendering, not a raw technical dump.
- Prefer this order:
  - title
  - one-sentence conclusion
  - one simple tree block
  - one detailed tree block when useful
  - one concise Markdown table
  - short calculation steps
  - formula code blocks
- The default table should be business-readable and tree-aware.
- Prefer dynamic layer columns such as `L1 | L2`, or `L1 | L2 | L3 | L4`, followed by `单元格 | 字段 | 值 | 作用说明`.
- Choose the number of `L` columns according to actual lineage depth. Do not force `L4` when only two layers exist.
- Do not put long formulas inside the main table unless the user explicitly asks for a technical view.
- Before the table, include a simple ASCII tree using `|__` style.
- The simple tree must still preserve real parent-child depth. Do not flatten all upstream nodes to the same indentation level.
- When it helps, also include a second detailed tree that shows matched source rows or fallback branches.
- Do not put the full `|__` tree directly inside the main table cells unless the user explicitly asks for a pure text matrix.
- Include direct precedents whenever they can be identified.
- Include recursive lineage only when it materially helps the user.
- Output Mermaid only when the user explicitly asks for a diagram or when the table alone is still too hard to follow.
- If the graph would be noisy, incomplete, or misleading, skip Mermaid and say why.
- When named ranges, spill formulas, SQL formulas, engine-specific behavior, or ambiguous deep chains are involved, explicitly mark uncertainty.

Keep the final answer concise. Prefer a short explanation plus a well-rendered Markdown table over long prose.
