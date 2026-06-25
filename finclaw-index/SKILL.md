---
name: finclaw-index
description: Routes FinClaw finance and accounting requests to the right workflow, including 文件接收, 财报分析, 结账分析, 差异分析, 审计复核, 数据溯源, dashboard, 情景模拟, and follow-up Q&A. Use when the task needs top-level intent routing, preflight decisions, capability gating, or selection of `traceable-financial-analysis` and related supporting skills.
version: 0.1.0
---

# FinClaw Index

This skill is the top-level router for the FinClaw finance and accounting workflow.

It owns:

- request classification
- preflight gating
- primary skill selection
- supporting skill selection
- delivery mode selection

It does not own business conclusions, workbook writes, or detailed financial analysis.

## Use when

Trigger this skill for:

- first-turn finance or accounting requests
- requests that may become formal report workflows
- file upload / path-based analysis requests
- requests that need routing between intake, analysis, validation, dashboard, simulation, or audit
- implementation or review of the FinClaw multi-skill architecture

## Do not use when

- the task is already clearly inside `traceable-financial-analysis`
- the task is already a low-level MaybeAI Sheet operation
- the task is a narrow formula-lineage implementation already owned by `maybeai-formula-report`

## Mandatory loading order

When this skill triggers:

1. Read `references/route-types.md`.
2. Read `references/handoff-contract.md`.
3. If the request is a finance workflow request, load `finclaw-user-context`.
4. If the request should become a formal finance workflow, route to `traceable-financial-analysis`.

## Routing rules

- Formal financial analysis, boss-review reports, audit review, traceability, or finance Q&A about a report:
  Route to `traceable-financial-analysis`.
- New file upload, folder path, unreadable documents, or source-format uncertainty:
  Route first to `finclaw-intake`.
- Source quality, period mismatch, missing fields, metric inconsistency, or validation-only asks:
  Route to `finclaw-validate-data`.
- Formula-driven report workbook requirements:
  Add `maybeai-formula-report` as a supporting skill after the domain route is clear.
- Generic worksheet operations:
  Add `maybeai-sheet` only as a supporting execution layer.

## Workflow summary

1. Classify the request into a route type.
2. Check whether preflight context is required.
3. Detect blocking gaps such as missing files, unclear entity scope, or unavailable source of truth.
4. Select one primary skill and the minimal supporting skills.
5. Choose a delivery mode such as conversation, MaybeAI workbook, dashboard, or export artifact.
6. Hand off through the route contract without inventing facts.

## Standard route output

The route result should be expressible with these keys:

- `request_type`
- `needs_preflight`
- `primary_skill`
- `supporting_skills`
- `delivery_mode`
- `blocking_gaps`
- `notes_for_handoff`

## Hard rules

1. Prefer `traceable-financial-analysis` as the primary domain workflow for formal finance work.
2. Do not directly modify or replace `finclaw-report-analysis` from this skill.
3. Do not perform deep analysis in the router.
4. Do not send the user into workbook execution before source scope is clear.
5. If the route is blocked, explain what is missing instead of guessing.

## Composition rules

- Use `finclaw-user-context` for saved preferences, source readiness, and preflight.
- Use `finclaw-intake` for file and path intake.
- Use `finclaw-validate-data` for source and metric checks.
- Use `traceable-financial-analysis` for business semantics, audit expectations, and formal report behavior.

