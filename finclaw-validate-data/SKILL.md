---
name: finclaw-validate-data
description: Validates FinClaw finance source quality and metric consistency, including 源完整性, 期间匹配, 单位规范, 三表勾稽, 字段映射, KPI 复核, and blocking vs non-blocking issue classification. Use when the workflow needs a validation gate before `traceable-financial-analysis`, delivery, or formula-driven workbook generation.
version: 0.1.0
---

# FinClaw Validate Data

This skill owns validation gates for finance source material and derived metrics.

It owns:

- source completeness checks
- period alignment checks
- unit normalization checks
- mapping and schema checks
- metric consistency and reconciliation checks
- severity classification for issues

It does not own user intake or final business conclusions.

## Use when

Trigger this skill for:

- source quality review before formal analysis
- metric or statement inconsistency
- period mismatch or unit mismatch
- validation-only finance requests
- pre-delivery audit gates

## Mandatory loading order

When this skill triggers:

1. Read `references/validation-gates.md`.
2. Read `references/issue-taxonomy.md`.
3. If the data is formal-report ready, hand off to `traceable-financial-analysis`.

## Workflow summary

1. Check source completeness and readability.
2. Confirm company, entity, period, and unit consistency.
3. Validate statement mappings and derived metric definitions.
4. Classify issues into blocking and non-blocking severities.
5. Return a compact validation verdict and next-step recommendation.

## Standard validation output

The validation result should be expressible with these keys:

- `validation_scope`
- `passed`
- `blocking_issues`
- `non_blocking_issues`
- `source_quality_summary`
- `metric_consistency_summary`
- `recommended_next_skill`

## Hard rules

1. Blocking issues must be visible, not hidden in prose.
2. Do not call a dataset ready when period, unit, or mapping ambiguity remains material.
3. Prefer deterministic checks and stable scripts when available.
4. Distinguish missing data from contradictory data.
5. Keep the verdict actionable for the next skill.

## Composition rules

- Use after `finclaw-intake` when readable sources exist.
- Use before `traceable-financial-analysis` for formal workflows whenever data quality is uncertain.
- Prefer existing stable checks such as `traceable-financial-analysis/scripts/validate_report.py` and `finclaw-three-statement-foundation/scripts/run_three_statement_foundation.py` when they fit the validation scope.
- Pass only reviewed facts forward to report and workbook layers.

