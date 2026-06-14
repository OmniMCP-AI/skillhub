---
name: analyze-sheet-lineage
description: Explains spreadsheet cell lineage, precedents, dependency chains, and available write-time sidecar provenance from a selected cell or range. Use when the user asks why a value appears, where a formula pulls from, what cells depend on what, or wants a dependency chain table for a workbook cell/range.
---

# Analyze Sheet Lineage

Use this skill for explanation-layer lineage work, not for building a new backend lineage API.

When MaybeAI source/confidence sidecar metadata exists, use it as provenance context for literal cells and externally generated values. Formula lineage still comes from workbook formulas; sidecar metadata supplements source/confidence explanation and must not replace confirmed formula precedents.

Shared contract: read `context-contract.md` first. It defines the input tags, the preferred selectors, the workflow boundary, and the minimum output.

## Trigger

Trigger when the user asks any of these:

- why a cell has its value
- which cells a formula depends on
- upstream / downstream / precedent / dependent / lineage / dependency chain
- sidecar provenance, source metadata, or confidence metadata for a lineage target
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
- Read `verification.md` when sidecar metadata is part of the explanation or when validating formula reads.

## Output Rules

- The default output is friendly Markdown for chat rendering, not a raw technical dump.
- Prefer this order:
  - title
  - one-sentence conclusion
  - one simple DAG block
  - one optional tree block when useful
  - one concise Markdown table only in deep explain mode
  - short calculation steps
  - formula code blocks
- The default diagram should be a business-readable ASCII DAG, similar to a lightweight flowchart:
  - node title line
  - boxed node content
  - labeled arrows between steps
- Put the default DAG inside one fenced `text` code block and keep box values inside the frame.
- Prefer the DAG to show the main path only. Keep side branches only when they materially improve understanding.
- The tree view is optional. Use it when the user asks for a tree, when the dependency graph branches heavily, or when plain indentation explains side branches better than the DAG.
- The detailed table is deep explain mode, not the default artifact.
- In deep explain mode, prefer dynamic layer columns such as `L1 | L2`, or `L1 | L2 | L3 | L4`, followed by `单元格 | 字段 | 公式 | 值 | 作用说明`.
- In deep explain mode, choose the number of `L` columns according to actual lineage depth. Do not force `L4` when only two layers exist.
- In deep explain mode, include one `公式` column in the main table. Use exact formulas for key formula rows and `literal` for literal rows.
- If a formula is too long for the table, keep a compact readable version in the table and place the full exact formula again in the formula code block section.
- Include direct precedents whenever they can be identified.
- Include sidecar source/confidence facts for literal or generated cells when available, but label them as metadata rather than formula precedents.
- Include recursive lineage only when it materially helps the user.
- Output Mermaid only when the user explicitly asks for a diagram or when the table alone is still too hard to follow.
- If the graph would be noisy, incomplete, or misleading, skip Mermaid and say why.
- When named ranges, spill formulas, SQL formulas, engine-specific behavior, or ambiguous deep chains are involved, explicitly mark uncertainty.

Keep the final answer concise. Prefer a short explanation plus a well-rendered DAG over long prose, and add the Markdown table only in deep explain mode.
