---
name: finclaw-user-context
description: Manages FinClaw finance user context and preflight state, including 公司画像, 主体范围, 会计口径, 默认模板, 常用 KPI, 数据源优先级, and source readiness. Use when the task needs saved finance context, preflight checks, source readiness evaluation, or repeated company-specific defaults before entering `traceable-financial-analysis`.
version: 0.1.0
---

# FinClaw User Context

This skill owns saved finance context and preflight evaluation for FinClaw workflows.

It owns:

- company profile memory
- entity and period defaults
- source readiness
- preferred templates and output modes
- known metric definitions and finance conventions

It does not own business analysis or final report writing.

## Use when

Trigger this skill when:

- a finance workflow may need company-specific defaults
- the source of truth may be unavailable or incomplete
- the same company or user will run repeated finance tasks
- the router needs to know whether work can start now
- the workflow needs remembered KPI definitions or report preferences

## Mandatory loading order

When this skill triggers:

1. Read `references/context-schema.md`.
2. Read `references/preflight-checklist.md`.
3. Return a context summary before the workflow enters `traceable-financial-analysis`.

## Workflow summary

1. Identify company, entity scope, and requested period.
2. Check whether the user or prior runs already define source priorities or template preferences.
3. Evaluate source readiness, permissions, and required missing inputs.
4. Normalize remembered metric definitions or note that they are unknown.
5. Return a compact context and preflight summary.

## Standard context output

The result should be expressible with these keys:

- `context_summary`
- `default_entity_scope`
- `default_period_rules`
- `source_readiness`
- `preferred_templates`
- `preferred_delivery_modes`
- `known_metric_defs`
- `missing_requirements`

## Hard rules

1. Do not fabricate remembered context.
2. If a context field is unknown, mark it unknown.
3. If a source is required but unavailable, say so clearly.
4. Keep preflight compact and decision-oriented.
5. Pass forward only useful context for the next skill.

## Composition rules

- `finclaw-index` should call this skill before routing formal finance work.
- `traceable-financial-analysis` should consume this skill's preflight summary, not re-ask every default question.
- `finclaw-intake` may add source-path and file-format facts that update this context.
- `finclaw-validate-data` may refine source readiness after validation.

