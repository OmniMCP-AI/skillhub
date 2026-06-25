---
name: finclaw-intake
description: Handles FinClaw finance file and path intake, including 上传文件, 文件夹路径, 报表格式识别, 初步可读性检查, and source-scope clarification. Use when the user provides finance files, needs supported-format guidance, or the workflow must establish source scope before `traceable-financial-analysis` or `finclaw-validate-data`.
version: 0.1.0
---

# FinClaw Intake

This skill owns the intake layer for finance source material.

It owns:

- file and path intake
- supported-format clarification
- source scope capture
- first-pass readability checks
- intake summary for downstream skills

It does not own full financial analysis or final report logic.

## Use when

Trigger this skill for:

- new finance file uploads
- folder-path based analysis requests
- unclear source formats
- unreadable or mixed-format source bundles
- the first step before validation or formal analysis

## User intake rule

When files are needed, use this prompt:

```text
可以，请把财报文件直接发给我，或者告诉我文件/文件夹在哪里。

Excel、CSV、PDF、Word、图片或压缩包都可以先发来；我会先检查文件能否读取，后续按默认流程处理。
```

Do not search arbitrary local disk locations before the user gives a path or confirms scope.

## Mandatory loading order

When this skill triggers:

1. Read `references/supported-inputs.md`.
2. Read `references/intake-decision-tree.md`.
3. If readable sources are present, hand off to `finclaw-validate-data` or `traceable-financial-analysis`.

## Workflow summary

1. Capture the file or folder scope from the user.
2. Determine whether the source type is supported now, delegated, or blocked.
3. Run first-pass readability checks or parser previews when appropriate.
4. Summarize what was received, what was readable, and what is missing.
5. Hand off to validation or analysis.

## Standard intake output

The intake result should be expressible with these keys:

- `source_scope`
- `received_files`
- `supported_now`
- `needs_delegation`
- `readability_status`
- `recommended_next_skill`
- `missing_inputs`

## Hard rules

1. Never imply that the entire local disk was searched automatically.
2. Do not claim unsupported scanned content was parsed if OCR was not actually available.
3. Keep intake questioning narrow; ask only for what is needed to continue.
4. Preserve the source path and file identity for downstream traceability.

## Composition rules

- Prefer `finclaw-financial-analysis-runner/scripts/finclaw-parse-upload.py` when the current repo parser is the right fit.
- Use `finclaw-validate-data` after readable sources are identified.
- Use `traceable-financial-analysis` when the workflow is ready to become formal finance analysis.

