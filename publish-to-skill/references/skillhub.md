# SkillHub Publishing

Read this file when the target is `skillhub`.

## Auth

Use the registry and token supplied in the current request. Do not write tokens into repo files.

```bash
skillhub whoami \
  --registry "$SKILLHUB_REGISTRY" \
  --token "$SKILLHUB_TOKEN" \
  --json
```

If the user wants the login stored locally:

```bash
skillhub login \
  --registry "$SKILLHUB_REGISTRY" \
  --token "$SKILLHUB_TOKEN" \
  --json
```

## Prepare A Clean Publish Directory

When publishing a repo root, first create a temp directory without `.git`, `.gitignore`, and local junk:

```bash
python3 scripts/prepare_publish_dir.py "$SKILL_PATH" --json
```

Use the returned `prepared_dir` for publish commands.

## Dry Run

Always dry-run first:

```bash
skillhub publish "$PREPARED_DIR" \
  --registry "$SKILLHUB_REGISTRY" \
  --token "$SKILLHUB_TOKEN" \
  --dry-run \
  --json
```

If namespace is not `global`, add `--namespace "$SKILLHUB_NAMESPACE"`.

If validation returns `Version already published`, edit the local skill's `SKILL.md` `version:` to the recommended next version, rebuild the prepared directory, and rerun the dry-run.

## Publish

```bash
skillhub publish "$PREPARED_DIR" \
  --registry "$SKILLHUB_REGISTRY" \
  --token "$SKILLHUB_TOKEN" \
  --json
```

Or with namespace:

```bash
skillhub publish "$PREPARED_DIR" \
  --registry "$SKILLHUB_REGISTRY" \
  --token "$SKILLHUB_TOKEN" \
  --namespace "$SKILLHUB_NAMESPACE" \
  --json
```

## Verify

`skillhub search` does not accept `--token`, so pass the token via env:

```bash
SKILLHUB_TOKEN="$SKILLHUB_TOKEN" skillhub search "$SKILL_SLUG" \
  --registry "$SKILLHUB_REGISTRY" \
  --json
```

## Fin Mirror Pattern

For the common "publish to fin" flow:

```bash
export SKILLHUB_REGISTRY="https://skillhub.fin.maybeai.cn"
export SKILLHUB_TOKEN="<runtime token>"
python3 scripts/prepare_publish_dir.py /path/to/skill --json
skillhub whoami --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --json
skillhub publish "$PREPARED_DIR" --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --dry-run --json
skillhub publish "$PREPARED_DIR" --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --json
```

If the user references `https://skillhub.int.maybeai.cn/space/ops/skillhub-cli`, treat that as the intended operational pattern, but use the locally installed `skillhub` CLI to execute it.
