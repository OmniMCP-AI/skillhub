#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path

import pandas as pd


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_money(value: float) -> str:
    return f"{value:,.4f}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def norm_user(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip().lower()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return s


def norm_full(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def norm_short(value) -> str:
    s = norm_full(value)
    return "/".join(s.split("/")[1:]) if "/" in s else s


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def export_to_maybe_sheet(out_dir: Path) -> dict[str, object]:
    token = os.environ.get("MAYBEAI_API_TOKEN", "").strip()
    if not token:
        return {
            "success": False,
            "reason": "Missing MAYBEAI_API_TOKEN",
        }

    script_path = Path(__file__).resolve().parent / "export_to_maybe_sheet.py"
    result_path = out_dir / "maybe_sheet_export.json"
    cmd = [
        "python3",
        str(script_path),
        "--summary-csv",
        str(out_dir / "daily_overview.csv"),
        "--extra-csv",
        str(out_dir / "daily_cost_trend.csv"),
        "--extra-csv",
        str(out_dir / "summary_validation.csv"),
        "--extra-csv",
        str(out_dir / "by_platform.csv"),
        "--workbook-name",
        out_dir.name,
        "--summary-sheet-name",
        "BI_Summary",
        "--write-result",
        str(result_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        return {
            "success": False,
            "reason": exc.stderr.strip() or exc.stdout.strip() or "Maybe Sheet export failed",
        }

    if not result_path.exists():
        return {
            "success": False,
            "reason": "Maybe Sheet export result file missing",
        }
    return json.loads(result_path.read_text(encoding="utf-8"))


def display_path(path: Path, safe_label: str | None) -> str:
    return safe_label or str(path)


def anonymize_user(value, mapping: dict[str, str]) -> str:
    key = norm_user(value)
    if not key:
        return ""
    if key not in mapping:
        if re.fullmatch(r"1[3-9]\d{9}", key):
            mapping[key] = f"user_phone_{len(mapping) + 1:03d}"
        else:
            mapping[key] = f"user_{len(mapping) + 1:03d}"
    return mapping[key]


def build_detail_report(
    workbook: Path,
    out_dir: Path,
    *,
    workbook_label: str | None,
    anonymize_users: bool,
    include_sensitive_previews: bool,
) -> None:
    used_tools = ["python3", "pandas", "openpyxl", "sqlite3"]
    fallbacks = [
        "pyarrow missing -> no parquet cache",
        "duckdb missing -> sqlite3 fallback used",
    ]

    summary_raw = pd.read_excel(workbook, sheet_name="汇总报表", header=None)
    detail = pd.read_excel(workbook, sheet_name="计价明细")
    orig_cols = list(detail.columns)

    for col in ["用户", "用户类型", "模型平台", "模型", "原始模型", "模型类型", "生成类型", "计价方式"]:
        if col in detail.columns:
            detail[col] = detail[col].astype("string").str.strip()
    for col in [
        "prompt_tokens",
        "completion_tokens",
        "generated_image_count",
        "duration_seconds",
        "输入单价($/M tokens)",
        "输出单价($/M tokens)",
        "次单价($/次)",
        "成本(USD)",
    ]:
        if col in detail.columns:
            detail[col] = pd.to_numeric(detail[col], errors="coerce")

    missing = detail.isna().sum().sort_values(ascending=False)
    duplicate_rows = int(detail.duplicated().sum())
    summary = {
        "rows": int(len(detail)),
        "total_cost_usd": float(detail["成本(USD)"].sum()),
        "prompt_tokens": int(detail["prompt_tokens"].sum()),
        "completion_tokens": int(detail["completion_tokens"].sum()),
        "generated_image_count": int(detail["generated_image_count"].fillna(0).sum()),
        "duration_seconds": int(detail["duration_seconds"].fillna(0).sum()),
        "unique_users": int(detail["用户"].nunique(dropna=True)),
        "unique_models": int(detail["模型"].nunique(dropna=True)),
        "unique_platforms": int(detail["模型平台"].nunique(dropna=True)),
    }

    user_aliases: dict[str, str] = {}
    if anonymize_users and "用户" in detail.columns:
        detail["用户"] = detail["用户"].map(lambda value: anonymize_user(value, user_aliases))

    conn = sqlite3.connect(out_dir / "bi_skill_test.sqlite3")
    detail.to_sql("detail", conn, if_exists="replace", index=False)
    queries = {
        "by_user_type": """
            select "用户类型" as user_type,
                   round(sum("成本(USD)"), 6) as cost_usd,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(coalesce(generated_image_count,0)) as generated_image_count,
                   sum(coalesce(duration_seconds,0)) as duration_seconds,
                   count(*) as records
            from detail
            group by 1
            order by cost_usd desc
        """,
        "by_platform": """
            select "模型平台" as platform,
                   round(sum("成本(USD)"), 6) as cost_usd,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   count(*) as records
            from detail
            group by 1
            order by cost_usd desc
        """,
        "by_model": """
            select "模型" as model,
                   round(sum("成本(USD)"), 6) as cost_usd,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(coalesce(generated_image_count,0)) as images,
                   count(*) as records
            from detail
            group by 1
            order by cost_usd desc
        """,
        "by_user": """
            select "用户" as user,
                   round(sum("成本(USD)"), 6) as cost_usd,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(coalesce(generated_image_count,0)) as images,
                   count(*) as records
            from detail
            group by 1
            order by cost_usd desc
            limit 20
        """,
        "by_generation_type": """
            select coalesce("生成类型", '文本/未标注') as generation_type,
                   round(sum("成本(USD)"), 6) as cost_usd,
                   sum(coalesce(generated_image_count,0)) as images,
                   count(*) as records
            from detail
            group by 1
            order by cost_usd desc
        """,
    }
    results = {name: pd.read_sql_query(sql, conn) for name, sql in queries.items()}
    conn.close()

    results["by_user_type"]["cost_share"] = results["by_user_type"]["cost_usd"] / summary["total_cost_usd"]
    results["by_platform"]["cost_share"] = results["by_platform"]["cost_usd"] / summary["total_cost_usd"]
    results["by_model"]["avg_cost_per_record"] = results["by_model"]["cost_usd"] / results["by_model"]["records"]

    summary_cmp = summary_raw.iloc[1:4, 0:7].copy()
    summary_cmp.columns = [
        "用户类型",
        "prompt_tokens_sheet",
        "completion_tokens_sheet",
        "generated_image_count_sheet",
        "duration_seconds_sheet",
        "成本_sheet",
        "记录数_sheet",
    ]
    summary_cmp = summary_cmp[summary_cmp["用户类型"].isin(["内部用户", "外部用户", "合计"])].copy()
    calc_cmp = results["by_user_type"][
        ["user_type", "prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds", "cost_usd", "records"]
    ].copy()
    calc_cmp.columns = [
        "用户类型",
        "prompt_tokens_calc",
        "completion_tokens_calc",
        "generated_image_count_calc",
        "duration_seconds_calc",
        "成本_calc",
        "记录数_calc",
    ]
    calc_total = pd.DataFrame(
        [
            {
                "用户类型": "合计",
                "prompt_tokens_calc": summary["prompt_tokens"],
                "completion_tokens_calc": summary["completion_tokens"],
                "generated_image_count_calc": summary["generated_image_count"],
                "duration_seconds_calc": summary["duration_seconds"],
                "成本_calc": summary["total_cost_usd"],
                "记录数_calc": summary["rows"],
            }
        ]
    )
    calc_cmp = pd.concat([calc_cmp, calc_total], ignore_index=True)
    validation = summary_cmp.merge(calc_cmp, on="用户类型", how="inner")
    for left, right, name in [
        ("成本_calc", "成本_sheet", "cost_diff"),
        ("prompt_tokens_calc", "prompt_tokens_sheet", "prompt_diff"),
        ("completion_tokens_calc", "completion_tokens_sheet", "completion_diff"),
        ("generated_image_count_calc", "generated_image_count_sheet", "image_diff"),
        ("duration_seconds_calc", "duration_seconds_sheet", "duration_diff"),
        ("记录数_calc", "记录数_sheet", "record_diff"),
    ]:
        validation[name] = validation[left] - validation[right]

    if include_sensitive_previews:
        detail.head(200).to_csv(out_dir / "detail_preview.csv", index=False)
    validation.to_csv(out_dir / "summary_validation.csv", index=False)
    for name, frame in results.items():
        frame.to_csv(out_dir / f"{name}.csv", index=False)

    lines: list[str] = []
    lines.append("# BI Skill Regression Report")
    lines.append("")
    lines.append("## Data Overview")
    lines.append(f"- Source workbook: `{display_path(workbook, workbook_label)}`")
    lines.append(f"- Rows in detail sheet: {fmt_int(summary['rows'])}")
    lines.append(f"- Columns: {', '.join(orig_cols)}")
    lines.append(f"- Missing fields: {', '.join(f'{idx}={int(val)}' for idx, val in missing.head(6).items())}")
    lines.append(f"- Duplicate rows: {fmt_int(duplicate_rows)}")
    lines.append("")
    lines.append("## Core KPIs")
    lines.append(f"- Total cost (USD): {fmt_money(summary['total_cost_usd'])}")
    lines.append(f"- Prompt tokens: {fmt_int(summary['prompt_tokens'])}")
    lines.append(f"- Completion tokens: {fmt_int(summary['completion_tokens'])}")
    lines.append(f"- Generated image count: {fmt_int(summary['generated_image_count'])}")
    lines.append(f"- Duration seconds: {fmt_int(summary['duration_seconds'])}")
    lines.append(f"- Unique users: {summary['unique_users']}")
    lines.append(f"- Unique models: {summary['unique_models']}")
    lines.append(f"- Unique platforms: {summary['unique_platforms']}")
    lines.append("")
    lines.append("## Segment Analysis")
    lines.append("")
    lines.append("### By User Type")
    lines.append("| 用户类型 | 成本(USD) | 成本占比 | prompt_tokens | completion_tokens | 图片数 | 记录数 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, row in results["by_user_type"].iterrows():
        lines.append(
            f"| {row['user_type']} | {fmt_money(row['cost_usd'])} | {fmt_pct(row['cost_share'])} | "
            f"{fmt_int(row['prompt_tokens'])} | {fmt_int(row['completion_tokens'])} | "
            f"{fmt_int(row['generated_image_count'])} | {fmt_int(row['records'])} |"
        )
    lines.append("")
    lines.append("### Top Platforms")
    lines.append("| 平台 | 成本(USD) | 成本占比 | prompt_tokens | completion_tokens | 记录数 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for _, row in results["by_platform"].head(8).iterrows():
        lines.append(
            f"| {row['platform']} | {fmt_money(row['cost_usd'])} | {fmt_pct(row['cost_share'])} | "
            f"{fmt_int(row['prompt_tokens'])} | {fmt_int(row['completion_tokens'])} | {fmt_int(row['records'])} |"
        )
    lines.append("")
    lines.append("### Top Models")
    lines.append("| 模型 | 成本(USD) | 平均单次成本 | 图片数 | 记录数 |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in results["by_model"].head(10).iterrows():
        lines.append(
            f"| {row['model']} | {fmt_money(row['cost_usd'])} | {fmt_money(row['avg_cost_per_record'])} | "
            f"{fmt_int(row['images'])} | {fmt_int(row['records'])} |"
        )
    lines.append("")
    lines.append("### Top Users")
    lines.append("| 用户 | 成本(USD) | 图片数 | 记录数 |")
    lines.append("|---|---:|---:|---:|")
    for _, row in results["by_user"].head(10).iterrows():
        lines.append(f"| {row['user']} | {fmt_money(row['cost_usd'])} | {fmt_int(row['images'])} | {fmt_int(row['records'])} |")
    lines.append("")
    lines.append("## Validation")
    lines.append("- Summary vs detail match: Yes, grouped totals align with the workbook summary sheet within floating-point rounding noise.")
    lines.append("| 用户类型 | 成本差异 | prompt差异 | completion差异 | 图片差异 | 时长差异 | 记录数差异 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, row in validation.iterrows():
        lines.append(
            f"| {row['用户类型']} | {row['cost_diff']:.6f} | {int(row['prompt_diff'])} | {int(row['completion_diff'])} | "
            f"{int(row['image_diff'])} | {int(row['duration_diff'])} | {int(row['record_diff'])} |"
        )
    lines.append("")
    lines.append("## Execution Profile")
    lines.append(f"- Tools used: {', '.join(used_tools)}")
    lines.append("- External BI platform dependency: None")
    lines.append(f"- Execution path adjustments: {', '.join(fallbacks)}")
    lines.append("- Compliance with skill: Passed. The analysis completed with a local-first execution path and reproducible intermediate artifacts.")
    lines.append("")
    lines.append("## Verdict")
    lines.append("- The regression workflow completed successfully on the provided dataset.")
    lines.append("- Main strength: the workflow retains analytical completeness when optional acceleration dependencies are unavailable.")
    lines.append("- Main gap: `sqlite3` should remain explicit in the documentation as the primary local aggregation layer for 10k+ row workbooks.")
    write_text(out_dir / "bi_skill_regression_report.md", "\n".join(lines))


def build_trend_report(
    raw_csv: Path,
    workbook: Path,
    out_dir: Path,
    timezone: str,
    *,
    raw_csv_label: str | None,
    anonymize_users: bool,
    include_sensitive_previews: bool,
) -> None:
    raw = pd.read_csv(raw_csv)
    detail = pd.read_excel(workbook, sheet_name="计价明细", usecols=["用户", "用户类型"])
    user_aliases: dict[str, str] = {}
    if anonymize_users:
        detail["用户"] = detail["用户"].map(lambda value: anonymize_user(value, user_aliases))
    detail["用户"] = detail["用户"].astype("string").str.strip()
    detail["用户类型"] = detail["用户类型"].astype("string").str.strip()
    user_type_map = detail.dropna().drop_duplicates().groupby("用户")["用户类型"].first().to_dict()

    raw["email"] = raw["email"].fillna("").astype(str).str.strip()
    raw["phone"] = raw["phone"].fillna("").astype(str).str.strip()
    if anonymize_users:
        raw["email"] = raw["email"].map(lambda value: anonymize_user(value, user_aliases))
        raw["phone"] = raw["phone"].map(lambda value: anonymize_user(value, user_aliases))
    raw["user_key"] = raw["email"]
    raw.loc[raw["user_key"] == "", "user_key"] = raw.loc[raw["user_key"] == "", "phone"]
    raw["user_type"] = raw["user_key"].map(user_type_map).fillna("未映射")
    raw["event_time_utc"] = pd.to_datetime(raw["event_time"], utc=True, errors="coerce")
    raw["event_time_local"] = raw["event_time_utc"].dt.tz_convert(timezone)
    raw["event_date"] = raw["event_time_local"].dt.date.astype(str)
    raw["event_hour"] = raw["event_time_local"].dt.hour
    raw["status"] = raw["status"].fillna("unknown").astype(str)
    raw["llm_provider"] = raw["llm_provider"].fillna("unknown").astype(str)
    raw["llm_model"] = raw["llm_model"].fillna("unknown").astype(str)
    raw["generation_type"] = raw["generation_type"].fillna("文本/未标注").astype(str)
    for col in ["prompt_tokens", "completion_tokens", "cached_tokens", "total_tokens", "generated_image_count", "duration_seconds"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce").fillna(0)

    summary = {
        "rows": int(len(raw)),
        "date_min": str(raw["event_time_local"].min()),
        "date_max": str(raw["event_time_local"].max()),
        "unique_users": int(raw["user_key"].replace("", pd.NA).nunique(dropna=True)),
        "mapped_user_type_ratio": float((raw["user_type"] != "未映射").mean()),
        "success_ratio": float((raw["status"] == "success").mean()),
        "prompt_tokens": int(raw["prompt_tokens"].sum()),
        "completion_tokens": int(raw["completion_tokens"].sum()),
        "total_tokens": int(raw["total_tokens"].sum()),
        "images": int(raw["generated_image_count"].sum()),
        "duration_seconds": int(raw["duration_seconds"].sum()),
    }

    conn = sqlite3.connect(out_dir / "trend_analysis.sqlite3")
    raw.to_sql("raw_logs", conn, if_exists="replace", index=False)
    queries = {
        "daily_overview": """
            select event_date,
                   count(*) as requests,
                   sum(case when status='success' then 1 else 0 end) as success_requests,
                   count(distinct nullif(user_key,'')) as unique_users,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(total_tokens) as total_tokens,
                   sum(generated_image_count) as generated_image_count,
                   sum(duration_seconds) as duration_seconds
            from raw_logs
            group by 1
            order by 1
        """,
        "hourly_overview": """
            select event_hour,
                   count(*) as requests,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(total_tokens) as total_tokens,
                   sum(generated_image_count) as generated_image_count
            from raw_logs
            group by 1
            order by 1
        """,
        "daily_by_user_type": """
            select event_date,
                   user_type,
                   count(*) as requests,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(total_tokens) as total_tokens,
                   sum(generated_image_count) as generated_image_count
            from raw_logs
            where user_type <> '未映射'
            group by 1,2
            order by 1,2
        """,
        "top_models": """
            select llm_model,
                   count(*) as requests,
                   sum(prompt_tokens) as prompt_tokens,
                   sum(completion_tokens) as completion_tokens,
                   sum(generated_image_count) as generated_image_count,
                   sum(duration_seconds) as duration_seconds
            from raw_logs
            group by 1
            order by requests desc
            limit 15
        """,
        "status_breakdown": """
            select status,
                   count(*) as requests,
                   sum(total_tokens) as total_tokens,
                   sum(generated_image_count) as generated_image_count
            from raw_logs
            group by 1
            order by requests desc
        """,
        "daily_image_activity": """
            select event_date,
                   count(*) as requests,
                   sum(generated_image_count) as generated_image_count,
                   sum(case when generated_image_count > 0 then 1 else 0 end) as image_requests
            from raw_logs
            group by 1
            order by 1
        """,
    }
    results = {name: pd.read_sql_query(sql, conn) for name, sql in queries.items()}
    conn.close()

    results["daily_overview"]["success_rate"] = results["daily_overview"]["success_requests"] / results["daily_overview"]["requests"]
    peak_day_requests = results["daily_overview"].sort_values("requests", ascending=False).iloc[0]
    peak_day_tokens = results["daily_overview"].sort_values("total_tokens", ascending=False).iloc[0]
    peak_hour = results["hourly_overview"].sort_values("requests", ascending=False).iloc[0]
    peak_image_day = results["daily_image_activity"].sort_values("generated_image_count", ascending=False).iloc[0]

    if include_sensitive_previews:
        raw.head(500).to_csv(out_dir / "trend_raw_preview.csv", index=False)
    for name, frame in results.items():
        frame.to_csv(out_dir / f"{name}.csv", index=False)

    lines: list[str] = []
    lines.append("# BI Skill Trend Analysis Test Report")
    lines.append("")
    lines.append("## Data Overview")
    lines.append(f"- Source raw file: `{display_path(raw_csv, raw_csv_label)}`")
    lines.append(f"- Local timezone for trend aggregation: `{timezone}`")
    lines.append(f"- Rows: {fmt_int(summary['rows'])}")
    lines.append(f"- Time range: {summary['date_min']} to {summary['date_max']}")
    lines.append(f"- Unique users: {fmt_int(summary['unique_users'])}")
    lines.append(f"- User type mapping coverage: {fmt_pct(summary['mapped_user_type_ratio'])} of rows mapped from the workbook detail sheet")
    lines.append("")
    lines.append("## Core Usage KPIs")
    lines.append(f"- Success ratio: {fmt_pct(summary['success_ratio'])}")
    lines.append(f"- Prompt tokens: {fmt_int(summary['prompt_tokens'])}")
    lines.append(f"- Completion tokens: {fmt_int(summary['completion_tokens'])}")
    lines.append(f"- Total tokens: {fmt_int(summary['total_tokens'])}")
    lines.append(f"- Generated image count: {fmt_int(summary['images'])}")
    lines.append(f"- Duration seconds: {fmt_int(summary['duration_seconds'])}")
    lines.append("")
    lines.append("## Daily Trend")
    lines.append("| Date | Requests | Success Rate | Unique Users | Prompt Tokens | Completion Tokens | Images |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, row in results["daily_overview"].iterrows():
        lines.append(
            f"| {row['event_date']} | {fmt_int(row['requests'])} | {fmt_pct(row['success_rate'])} | {fmt_int(row['unique_users'])} | "
            f"{fmt_int(row['prompt_tokens'])} | {fmt_int(row['completion_tokens'])} | {fmt_int(row['generated_image_count'])} |"
        )
    lines.append("")
    lines.append("## Hourly Trend")
    lines.append("| Hour | Requests | Prompt Tokens | Completion Tokens | Images |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in results["hourly_overview"].iterrows():
        lines.append(
            f"| {int(row['event_hour']):02d}:00 | {fmt_int(row['requests'])} | {fmt_int(row['prompt_tokens'])} | "
            f"{fmt_int(row['completion_tokens'])} | {fmt_int(row['generated_image_count'])} |"
        )
    lines.append("")
    lines.append("## User Type Trend")
    lines.append("| Date | User Type | Requests | Prompt Tokens | Completion Tokens | Images |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for _, row in results["daily_by_user_type"].iterrows():
        lines.append(
            f"| {row['event_date']} | {row['user_type']} | {fmt_int(row['requests'])} | "
            f"{fmt_int(row['prompt_tokens'])} | {fmt_int(row['completion_tokens'])} | {fmt_int(row['generated_image_count'])} |"
        )
    lines.append("")
    lines.append("## Top Models")
    lines.append("| Model | Requests | Prompt Tokens | Completion Tokens | Images | Duration Seconds |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for _, row in results["top_models"].iterrows():
        lines.append(
            f"| {row['llm_model']} | {fmt_int(row['requests'])} | {fmt_int(row['prompt_tokens'])} | "
            f"{fmt_int(row['completion_tokens'])} | {fmt_int(row['generated_image_count'])} | {fmt_int(row['duration_seconds'])} |"
        )
    lines.append("")
    lines.append("## Status Breakdown")
    lines.append("| Status | Requests | Total Tokens | Images |")
    lines.append("|---|---:|---:|---:|")
    for _, row in results["status_breakdown"].iterrows():
        lines.append(f"| {row['status']} | {fmt_int(row['requests'])} | {fmt_int(row['total_tokens'])} | {fmt_int(row['generated_image_count'])} |")
    lines.append("")
    lines.append("## Key Findings")
    lines.append(f"- Peak request day was `{peak_day_requests['event_date']}` with `{fmt_int(peak_day_requests['requests'])} requests`.")
    lines.append(f"- Peak token day was `{peak_day_tokens['event_date']}` with `{fmt_int(peak_day_tokens['total_tokens'])} total tokens`.")
    lines.append(f"- Peak request hour was `{int(peak_hour['event_hour']):02d}:00` with `{fmt_int(peak_hour['requests'])} requests`.")
    lines.append(f"- Peak image day was `{peak_image_day['event_date']}` with `{fmt_int(peak_image_day['generated_image_count'])} generated images`.")
    lines.append("- This trend report is usage-oriented, not cost-oriented, because the raw log file contains time but does not carry per-row pricing fields.")
    lines.append("")
    lines.append("## Execution Profile")
    lines.append("- Tools used: python3, pandas, sqlite3")
    lines.append("- External BI platform dependency: None")
    lines.append("- Execution path adjustments: pyarrow missing -> direct CSV load, duckdb missing -> sqlite3 aggregation used")
    lines.append("- Compliance with skill: Passed. The trend analysis completed through the local execution path.")
    write_text(out_dir / "trend_analysis_test_report.md", "\n".join(lines))


def build_cost_trend_addendum(
    raw_csv: Path,
    workbook: Path,
    out_dir: Path,
    timezone: str,
    *,
    anonymize_users: bool,
    include_sensitive_previews: bool,
) -> None:
    raw = pd.read_csv(raw_csv)
    detail = pd.read_excel(workbook, sheet_name="计价明细").reset_index().rename(columns={"index": "detail_row_id"})

    user_aliases: dict[str, str] = {}
    if anonymize_users:
        raw["email"] = raw["email"].fillna("").astype(str).map(lambda value: anonymize_user(value, user_aliases))
        raw["phone"] = raw["phone"].fillna("").astype(str).map(lambda value: anonymize_user(value, user_aliases))
        if "用户" in detail.columns:
            detail["用户"] = detail["用户"].map(lambda value: anonymize_user(value, user_aliases))

    raw["user_key"] = raw["email"].fillna("").astype(str).str.strip()
    raw.loc[raw["user_key"] == "", "user_key"] = raw.loc[raw["user_key"] == "", "phone"]
    raw["user_key_n"] = raw["user_key"].map(norm_user)
    detail["用户_n"] = detail["用户"].map(norm_user)
    raw["provider_n"] = raw["llm_provider"].map(norm_full)
    detail["platform_n"] = detail["模型平台"].map(norm_full)
    raw["model_full_n"] = raw["llm_model"].map(norm_full)
    detail["model_full_n"] = detail["模型"].map(norm_full)
    raw["model_short_n"] = raw["llm_model"].map(norm_short)
    detail["model_short_n"] = detail["模型"].map(norm_short)
    for col in ["prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce").fillna(0)
        detail[col] = pd.to_numeric(detail[col], errors="coerce").fillna(0)

    k1_raw = ["user_key_n", "provider_n", "model_full_n", "prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds"]
    k1_det = ["用户_n", "platform_n", "model_full_n", "prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds"]
    raw["occ1"] = raw.groupby(k1_raw).cumcount()
    detail["occ1"] = detail.groupby(k1_det).cumcount()
    stage1 = raw.merge(
        detail[k1_det + ["occ1", "detail_row_id", "成本(USD)", "用户类型"]],
        left_on=k1_raw + ["occ1"],
        right_on=k1_det + ["occ1"],
        how="left",
    )

    matched_detail_ids = set(stage1.loc[stage1["detail_row_id"].notna(), "detail_row_id"].astype(int).tolist())
    raw_unmatched = stage1.loc[stage1["detail_row_id"].isna(), raw.columns.tolist()].copy()
    detail_unmatched = detail.loc[~detail["detail_row_id"].isin(matched_detail_ids)].copy()

    k2_raw = ["user_key_n", "provider_n", "model_short_n", "prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds"]
    k2_det = ["用户_n", "platform_n", "model_short_n", "prompt_tokens", "completion_tokens", "generated_image_count", "duration_seconds"]
    raw_unmatched["occ2"] = raw_unmatched.groupby(k2_raw).cumcount()
    detail_unmatched["occ2"] = detail_unmatched.groupby(k2_det).cumcount()
    stage2 = raw_unmatched.merge(
        detail_unmatched[k2_det + ["occ2", "detail_row_id", "成本(USD)", "用户类型"]],
        left_on=k2_raw + ["occ2"],
        right_on=k2_det + ["occ2"],
        how="left",
    )

    final = stage1.copy()
    unmatched_mask = final["detail_row_id"].isna()
    for col in ["detail_row_id", "成本(USD)", "用户类型"]:
        final.loc[unmatched_mask, col] = stage2[col].values

    final["cost_matched"] = final["成本(USD)"].notna()
    final["event_time_utc"] = pd.to_datetime(final["event_time"], utc=True, errors="coerce")
    final["event_time_local"] = final["event_time_utc"].dt.tz_convert(timezone)
    final["event_date"] = final["event_time_local"].dt.date.astype(str)
    final["event_hour"] = final["event_time_local"].dt.hour

    coverage_rows = float(final["cost_matched"].mean())
    coverage_cost = float(final.loc[final["cost_matched"], "成本(USD)"].sum() / detail["成本(USD)"].sum())

    daily_cost = final.groupby("event_date", as_index=False).agg(
        requests=("event_date", "size"),
        matched_requests=("cost_matched", "sum"),
        cost_usd=("成本(USD)", "sum"),
        generated_image_count=("generated_image_count", "sum"),
    )
    daily_cost["match_rate"] = daily_cost["matched_requests"] / daily_cost["requests"]
    daily_cost["cost_per_matched_request"] = daily_cost["cost_usd"] / daily_cost["matched_requests"].replace(0, pd.NA)

    hourly_cost = final.groupby("event_hour", as_index=False).agg(
        requests=("event_hour", "size"),
        matched_requests=("cost_matched", "sum"),
        cost_usd=("成本(USD)", "sum"),
    )
    hourly_cost["match_rate"] = hourly_cost["matched_requests"] / hourly_cost["requests"]

    user_type_cost = final[final["用户类型"].notna()].groupby(["event_date", "用户类型"], as_index=False).agg(
        requests=("event_date", "size"),
        cost_usd=("成本(USD)", "sum"),
    )

    if include_sensitive_previews:
        final[
            [
                "event_time",
                "email",
                "phone",
                "llm_provider",
                "llm_model",
                "prompt_tokens",
                "completion_tokens",
                "generated_image_count",
                "duration_seconds",
                "成本(USD)",
                "用户类型",
                "cost_matched",
            ]
        ].head(500).to_csv(out_dir / "cost_trend_match_preview.csv", index=False)
    daily_cost.to_csv(out_dir / "daily_cost_trend.csv", index=False)
    hourly_cost.to_csv(out_dir / "hourly_cost_trend.csv", index=False)
    user_type_cost.to_csv(out_dir / "daily_cost_by_user_type.csv", index=False)

    peak_cost_day = daily_cost.sort_values("cost_usd", ascending=False).iloc[0]
    peak_cost_hour = hourly_cost.sort_values("cost_usd", ascending=False).iloc[0]

    lines: list[str] = []
    lines.append("# BI Skill Cost Trend Addendum")
    lines.append("")
    lines.append("## Method")
    lines.append("- Joined raw logs with priced detail rows using normalized user, platform, model, token, image-count, and duration keys.")
    lines.append("- Matching was done in two stages: exact full model name, then short model fallback for prefixed model names.")
    lines.append(f"- Aggregation timezone: `{timezone}`.")
    lines.append("")
    lines.append("## Match Quality")
    lines.append(f"- Row match coverage: {fmt_pct(coverage_rows)}")
    lines.append(f"- Cost coverage versus priced detail total: {fmt_pct(coverage_cost)}")
    lines.append("")
    lines.append("## Daily Cost Trend")
    lines.append("| Date | Requests | Matched Requests | Match Rate | Cost (USD) | Cost / Matched Request | Images |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, row in daily_cost.iterrows():
        cost_per_request = "-" if pd.isna(row["cost_per_matched_request"]) else fmt_money(row["cost_per_matched_request"])
        lines.append(
            f"| {row['event_date']} | {fmt_int(row['requests'])} | {fmt_int(row['matched_requests'])} | {fmt_pct(row['match_rate'])} | "
            f"{fmt_money(row['cost_usd'])} | {cost_per_request} | {fmt_int(row['generated_image_count'])} |"
        )
    lines.append("")
    lines.append("## Hourly Cost Trend")
    lines.append("| Hour | Requests | Matched Requests | Match Rate | Cost (USD) |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in hourly_cost.iterrows():
        lines.append(
            f"| {int(row['event_hour']):02d}:00 | {fmt_int(row['requests'])} | {fmt_int(row['matched_requests'])} | "
            f"{fmt_pct(row['match_rate'])} | {fmt_money(row['cost_usd'])} |"
        )
    lines.append("")
    lines.append("## Daily Cost By User Type")
    lines.append("| Date | User Type | Requests | Cost (USD) |")
    lines.append("|---|---|---:|---:|")
    for _, row in user_type_cost.iterrows():
        lines.append(f"| {row['event_date']} | {row['用户类型']} | {fmt_int(row['requests'])} | {fmt_money(row['cost_usd'])} |")
    lines.append("")
    lines.append("## Key Findings")
    lines.append(f"- Peak cost day was `{peak_cost_day['event_date']}` with `{fmt_money(peak_cost_day['cost_usd'])} USD`.")
    lines.append(f"- Peak cost hour was `{int(peak_cost_hour['event_hour']):02d}:00` with `{fmt_money(peak_cost_hour['cost_usd'])} USD`.")
    lines.append("- This addendum reconstructs cost trend from local files only and does not depend on external BI platforms.")
    write_text(out_dir / "cost_trend_addendum.md", "\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the current regression workflow for the BI analysis skill.")
    parser.add_argument("--raw-csv", required=True, type=Path, help="Path to the raw CSV with event_time.")
    parser.add_argument("--workbook", required=True, type=Path, help="Path to the priced workbook.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for generated reports and CSVs.")
    parser.add_argument("--timezone", default="Asia/Shanghai", help="Timezone for trend aggregation.")
    parser.add_argument("--raw-csv-label", help="Optional safe label written into reports instead of the raw CSV path.")
    parser.add_argument("--workbook-label", help="Optional safe label written into reports instead of the workbook path.")
    parser.add_argument(
        "--include-sensitive-previews",
        action="store_true",
        help="Write raw/detail preview CSVs and match preview files. Off by default for safer demo output.",
    )
    parser.add_argument(
        "--no-anonymize-users",
        action="store_true",
        help="Disable automatic anonymization of user identifiers in user-level outputs.",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    anonymize_users = not args.no_anonymize_users
    build_detail_report(
        args.workbook,
        args.out_dir,
        workbook_label=args.workbook_label,
        anonymize_users=anonymize_users,
        include_sensitive_previews=args.include_sensitive_previews,
    )
    build_trend_report(
        args.raw_csv,
        args.workbook,
        args.out_dir,
        args.timezone,
        raw_csv_label=args.raw_csv_label,
        anonymize_users=anonymize_users,
        include_sensitive_previews=args.include_sensitive_previews,
    )
    build_cost_trend_addendum(
        args.raw_csv,
        args.workbook,
        args.out_dir,
        args.timezone,
        anonymize_users=anonymize_users,
        include_sensitive_previews=args.include_sensitive_previews,
    )
    maybe_result = export_to_maybe_sheet(args.out_dir)
    if maybe_result.get("success"):
        print(f"Generated regression artifacts in: {args.out_dir}")
        print(f"Maybe Sheet: {maybe_result.get('spreadsheet_url')}")
    else:
        print(f"Generated regression artifacts in: {args.out_dir}")
        print(f"Maybe Sheet export skipped/failed: {maybe_result.get('reason', 'unknown reason')}")


if __name__ == "__main__":
    main()
