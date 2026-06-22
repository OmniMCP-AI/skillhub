---
name: publish-to-skill
description: Publish or update a local skill to SkillHub or ClawHub. Use when a user wants to release a skill, mirror a skill between registries, validate publish readiness, or choose the next version from recent changes instead of guessing patch vs feature bumps.
---

# Publish To Skill

Use this skill when publishing a local skill folder to `skillhub` or `clawhub`.

## Quick Start

1. Identify the target:
   - `skillhub` for SkillHub registries such as `int` or `fin`
   - `clawhub` for ClawHub publish flows
2. Read the current version from the target skill's `SKILL.md`.
3. Run:

```bash
python3 scripts/recommend_version.py /path/to/skill --json
```

4. Use the recommended bump unless the user explicitly overrides it.
5. If the user wants an actual release, update the local version source first:
   - SkillHub: update `SKILL.md` `version:` before publish
   - ClawHub: keep repo version metadata aligned with the explicit `--version` you publish
6. For `skillhub`, read `references/skillhub.md`.
7. For `clawhub`, read `references/clawhub.md`.
8. Publish, then verify the result from CLI output or a follow-up search/inspect call.

## Version Policy

Base the release decision on changes since the most recent version-bump or release commit.

- `major`: only when a breaking change is explicit
- `minor`: new capability, new workflow, new API coverage, or a true feature commit such as `feat: ...`
- `patch`: fixes, refactors, docs, examples, prompt cleanup, packaging fixes, or behavior-preserving maintenance
- `none`: no unpublished changes worth releasing

Ignore pure version-bump commits such as `update ver`, `upgrade ver`, `bump version`, or `release`.

If the user asks for "fix or feature", map:

- `patch` -> `fix: ...`
- `minor` -> `feat: ...`

## SkillHub Workflow

Use the local `skillhub` CLI. Mirror the `ops/skillhub-cli` operational flow locally:

1. Validate auth with `whoami`
2. Prepare a clean publish directory if the source path is a repo root
3. Run `publish --dry-run`
4. Run the real `publish`
5. Verify with `search` or the returned detail URL

Always prepare a clean directory before publishing repo roots, because SkillHub validation commonly rejects `.git`, `.gitignore`, and local artifacts.
If dry-run returns `Version already published`, update the local `SKILL.md` `version:` to the recommended next version and dry-run again.

Read `references/skillhub.md` before acting.

## ClawHub Workflow

Use the local `clawhub` CLI.

1. Authenticate with `clawhub auth login`
2. Recommend the next version
3. Update local version metadata if the repo tracks it
4. Publish with explicit `--slug`, `--version`, `--changelog`, and `--tags`
5. Verify with `clawhub whoami`, `inspect`, or the publish result

Read `references/clawhub.md` before acting.

## Scripts

- `scripts/recommend_version.py`
  - Recommends `major`, `minor`, `patch`, or `none`
  - Parses the current version from `SKILL.md` when possible
  - Uses recent commits plus uncommitted changes
  - Ignores pure version-bump commits
- `scripts/prepare_publish_dir.py`
  - Copies a publish-safe skill directory to a temp folder
  - Excludes dotfiles, VCS metadata, caches, and common junk
  - Use this before `skillhub publish` on repo roots

## Operating Rules

- Never store registry tokens inside the skill files.
- Accept tokens from the current user request, CLI flags, or environment variables at runtime.
- Prefer `--dry-run` before remote publish when the CLI supports it.
- If the remote already has the same version, either bump again or stop and explain why.
- If the source repo has no meaningful changes since the last version bump, do not invent a release.

## When To Read References

- `references/skillhub.md`: SkillHub auth, dry-run, publish, and fin mirror commands
- `references/clawhub.md`: ClawHub auth and publish command patterns
- `references/versioning.md`: heuristics behind patch vs feature decisions
