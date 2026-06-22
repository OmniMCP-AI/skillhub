# Versioning Heuristics

Read this file when the user asks why the bump is `patch` vs `minor`.

## Decision Window

Look at commits since the most recent version-bump or release commit. Examples of commits to ignore as the boundary:

- `update ver`
- `upgrade ver`
- `bump version`
- `release 0.6.0`

## Recommended Mapping

- `major`
  - explicit breaking change
  - incompatible rename or behavior change called out in commit text
- `minor`
  - `feat: ...`
  - new endpoint coverage
  - new workflow
  - new helper script that adds a new supported capability
- `patch`
  - `fix: ...`
  - docs, prompt edits, references refactor
  - packaging fixes
  - example or sample correction
  - behavior-preserving cleanup
- `none`
  - no meaningful change since the last release commit

## Changelog Suggestions

When the user wants a short changelog:

- `major` -> use a direct breaking-change summary
- `minor` -> prefix with `feat:`
- `patch` -> prefix with `fix:`

## MaybeAI Sheet Example

If the recent unpublished work is something like:

- `Refactor skill docs for progressive disclosure`

and the prior commit is:

- `update ver`

recommend a `patch` bump, not a `minor` bump.
