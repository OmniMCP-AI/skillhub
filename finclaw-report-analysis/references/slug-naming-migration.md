# FinClaw Slug Naming and Migration Notes

## Canonical naming

FinClaw is a single product name. Runtime skill references should use `finclaw-*`, not the old split form `fin-claw-*`.

Canonical local coordinates:

- `data-reporting/finclaw-report-analysis`
- `data-reporting/finclaw-financial-analysis-runner`
- `financial-statements/finclaw-three-statement-foundation`
- `data-reporting/finclaw-mock-data`

Canonical SkillHub slugs:

- `data-reporting--finclaw-report-analysis`
- `data-reporting--finclaw-financial-analysis-runner`
- `financial-statements--finclaw-three-statement-foundation`
- `data-reporting--finclaw-mock-data`

## Migration rule

When updating FinClaw routing, role, capability, or report-analysis skill references, replace old runtime-chain references:

- `data-reporting/fin-claw-report-analysis` → `data-reporting/finclaw-report-analysis`
- `data-reporting/fin-claw-financial-analysis-runner` → `data-reporting/finclaw-financial-analysis-runner`
- `financial-statements/fin-claw-three-statement-foundation` → `financial-statements/finclaw-three-statement-foundation`
- `data-reporting/fin-claw-mock-data` → `data-reporting/finclaw-mock-data`

Prefer updating runtime-loading surfaces first: router configs, capability registries, role configs, required-skill lists, and user-facing entry contracts.

## What not to rewrite

Do not bulk-edit historical evaluation artifacts, old reports, usage logs, cache files, backup directories, or one-off prior-run notes just to normalize naming. Those records are evidence of past runs and should remain stable unless they actively affect loading or routing.

## Verification checklist

After migration:

1. Load all four canonical skills successfully.
2. Search runtime-chain configs and active skill references for old local coordinates.
3. Parse YAML configs touched during migration.
4. Confirm `finclaw-report-analysis` still points to `references/contract.md` and keeps the FIN_STMT / REAL_OPS / SYNTHETIC_DEMO / GAP separation rules.
5. If operating data is available, confirm the contract still requires a visible operating-driver front sheet/module rather than burying operating data in summaries or workpapers only.
