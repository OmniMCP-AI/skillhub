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

## Sync Main Before Version Edit

Before editing `SKILL.md` for a release, make sure the version bump is based on `origin/main`:

```bash
git -C "$SKILL_PATH" status --short --branch
git -C "$SKILL_PATH" checkout main
git -C "$SKILL_PATH" pull --ff-only origin main
```

If checkout or pull would overwrite unrelated local changes, stop and report the conflict. Do not stash, reset, or force-push as part of publishing.

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

## Commit And Push Version Bump

After publish and verification, persist the local version edit:

```bash
git -C "$SKILL_PATH" status --short --branch
git -C "$SKILL_PATH" add SKILL.md
git -C "$SKILL_PATH" commit -m "chore: bump $SKILL_SLUG to $NEXT_VERSION"
git -C "$SKILL_PATH" push origin main
```

Rules:

- Commit only version metadata files such as `SKILL.md`; do not add artifacts, prepared publish dirs, tokens, or unrelated user changes.
- If the skill repo is not on `main`, move to `main` before editing when the working tree allows it; otherwise stop and explain the branch conflict.
- If `git pull --ff-only origin main` fails, do not force-push. Resolve or report the divergence.
- If there is no version edit to commit, skip this step and say so.

## Fin Mirror Pattern

For the common "publish to fin" flow:

```bash
export SKILLHUB_REGISTRY="https://skillhub.fin.maybeai.cn"
export SKILLHUB_TOKEN="<runtime token>"
git -C /path/to/skill checkout main
git -C /path/to/skill pull --ff-only origin main
python3 scripts/prepare_publish_dir.py /path/to/skill --json
skillhub whoami --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --json
skillhub publish "$PREPARED_DIR" --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --dry-run --json
skillhub publish "$PREPARED_DIR" --registry "$SKILLHUB_REGISTRY" --token "$SKILLHUB_TOKEN" --json
SKILLHUB_TOKEN="$SKILLHUB_TOKEN" skillhub search "$SKILL_SLUG" --registry "$SKILLHUB_REGISTRY" --json
git -C /path/to/skill add SKILL.md
git -C /path/to/skill commit -m "chore: bump $SKILL_SLUG to $NEXT_VERSION"
git -C /path/to/skill push origin main
```

If the user references `https://skillhub.int.maybeai.cn/space/ops/skillhub-cli`, treat that as the intended operational pattern, but use the locally installed `skillhub` CLI to execute it.
