# Handoff Contract

The router should hand off with a compact structured envelope:

```text
request_type:
needs_preflight:
primary_skill:
supporting_skills:
delivery_mode:
blocking_gaps:
notes_for_handoff:
```

Guidelines:

- `primary_skill` should usually be one skill.
- `supporting_skills` should be minimal.
- `blocking_gaps` should be concrete, not vague.
- `notes_for_handoff` should include only route-critical facts such as company, period, source path, and missing inputs.

