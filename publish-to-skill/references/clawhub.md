# ClawHub Publishing

Read this file when the target is `clawhub`.

## Auth

Do not store the token in the skill files.

```bash
clawhub auth login --token "$CLAWHUB_TOKEN" --no-browser
clawhub whoami
```

If the user also provides custom site or registry endpoints, pass them through the CLI global flags.

## Publish

ClawHub publish should be explicit:

```bash
clawhub publish "$SKILL_PATH" \
  --slug "$SKILL_SLUG" \
  --version "$NEXT_VERSION" \
  --changelog "$CHANGELOG" \
  --tags "latest"
```

If the repo also stores the version in `SKILL.md`, update that file before publishing so the source tree matches the released version.

Keep the changelog aligned to the recommended bump:

- patch -> `fix: ...`
- minor -> `feat: ...`

## Example Pattern

This matches the common command shape the user may provide:

```bash
clawhub publish ~/work/ai/maybeai-uni/mcp/maybeai-sheet-skill \
  --slug "maybeai-sheet-skill" \
  --version 0.4.4 \
  --changelog "fix: upload excel" \
  --tags "latest"
```

The skill should not blindly reuse the example version. Recompute the next version from the current repo state first.
