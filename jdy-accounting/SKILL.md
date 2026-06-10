---
name: jdy-accounting
description: Automates JDY accounting report downloads and voucher Excel imports using bundled scripts. Also suitable for Chinese requests about 金蝶/精斗云财务、报表导出、凭证导入、上传凭证模板, or operating the JDY/KIS Cloud page with an existing Chrome login.
allowed-tools: Bash(uv:*)
---

# JDY Accounting Automation

这个 skill 也适用于中文场景里的 `金蝶`、`精斗云`、`金蝶云·星辰/精斗云财务`、`报表导出`、`凭证导入`、`上传凭证模板` 等请求。

当用户用中文提到这些关键词，通常应联想到这个 skill：

- `导出金蝶报表` / `下载精斗云报表`
- `导入凭证` / `上传凭证模板`
- `操作金蝶财务页面`
- `KIS Cloud` / `JDY accounting`

Use this skill's bundled `scripts/` for JDY work. These flows depend on an authenticated local Chrome profile, so prefer deterministic script execution over ad hoc browser steps.

## Prerequisites

- Use `uv`; do not use `pip`.
- Run commands from the directory that contains this `SKILL.md`, so `scripts/jdy_report_export.py` and `scripts/jdy_voucher_import.py` resolve correctly.
- Default Chrome profile is `Profile 3`. Change `--profile` only when the user specifies another profile or the default is not logged in.
- If proxy environment variables break local browser-use/httpx execution, unset them for the command with `env -u ALL_PROXY -u all_proxy -u HTTP_PROXY -u http_proxy -u HTTPS_PROXY -u https_proxy -u SOCKS_PROXY -u socks_proxy`.

## Download JDY Reports

Use `scripts/jdy_report_export.py` to export the configured report set for a period:

```bash
uv run --with browser-use --with requests python scripts/jdy_report_export.py --period YYYYMM --output-dir ./output/jdy-reports --profile "Profile 3"
```

If the user does not specify a period, omit `--period`; the script defaults to last month.

Success output prints each report as `OK` with a saved `.xlsx` path. Any `ERROR` line means that report failed and should be reported with the exact message.

## Import Voucher Template

Use `scripts/jdy_voucher_import.py` to open JDY, enter `查凭证 -> 导入`, upload the Excel template, choose the duplicate-voucher strategy, and confirm:

```bash
uv run --with browser-use --with requests python scripts/jdy_voucher_import.py --file <voucher-template.xlsx> --profile "Profile 3" --duplicate-strategy "重新编号"
```

If the user gives only a filename, search common user download locations first and pass the resolved file path to `--file`. Do not hardcode a machine-specific absolute path in the skill.

For the known template filename, use this pattern after resolving the file location:

```bash
uv run --with browser-use --with requests python scripts/jdy_voucher_import.py --file <resolved-path-to-20260605165228_凭证导入模板.xlsx> --profile "Profile 3" --duplicate-strategy "重新编号"
```

Success output includes text like `成功89条, 失败0条`. Report both numbers exactly. If the script prints full page text instead, inspect it for validation or error messages before claiming success.

## When Login Or Browser Fails

- If the script cannot read JDY auth state, ask the user to log into JDY in the target Chrome profile, then rerun.
- If attaching to an already-open Chrome fails, use the script's profile-based browser launch rather than Codex browser tooling.
- If temp Chrome profile copies consume disk space, remove only Browser Use temp profile directories named `browser-use-user-data-dir-*` under the system temp directory, then rerun.
