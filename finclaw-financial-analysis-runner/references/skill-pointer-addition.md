# SKILL.md pointer update (manual patch needed)

In `/root/.hermes/skills/data-reporting/finclaw-financial-analysis-runner/SKILL.md`, add this line **before** the `**Template column names`** section (around line 283, after the existing rule block that ends with `...fallback to delivering the local xlsx file directly`):

```
> **Fallback when quarter_metrics/computed_data are null:** rebuild from `statement_facts.json` — see `references/rebuild-metrics-from-facts.md`
```

Context: the inline update during session 2026-06-01 failed because `patch` tool is blocked by background review in this session.
