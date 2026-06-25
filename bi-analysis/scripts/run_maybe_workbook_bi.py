#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import subprocess
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_URL = "https://a-play-be.maybeai.cn/api/v1/excel"
WORKBOOK_URI = "https://www.maybe.ai/docs/spreadsheets/d/6a06dd0967ef87f2396711ac"
DEFAULT_OUTPUT_DIR = Path("/Users/duke/projects/skill-project/outputs/maybe-sheet-bi-6a06dd0967ef87f2396711ac")
DEFAULT_DASHBOARD_NAME = "经营总览Dashboard"
STYLE_RUNTIME_SCRIPT = Path("/Users/duke/projects/skill-project/analysis-style-match-skill/scripts/style_runtime.py")
INFOGRAPHIC_RENDER_SCRIPT = Path("/Users/duke/projects/skill-project/infographic-report-skill/scripts/render_from_presentation_payload.py")


def load_style_runtime():
    spec = importlib.util.spec_from_file_location("style_runtime", STYLE_RUNTIME_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load style runtime from {STYLE_RUNTIME_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STYLE_RUNTIME = load_style_runtime()
infer_industry_style = STYLE_RUNTIME.infer_industry_style
build_style_config = STYLE_RUNTIME.build_style_config
style_config_to_matrix = STYLE_RUNTIME.style_config_to_matrix
build_presentation_payload = STYLE_RUNTIME.build_presentation_payload


def get_token() -> str:
    token = os.environ.get("MAYBEAI_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("Missing MAYBEAI_API_TOKEN")
    return token


def post_json(path: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def read_sheet(uri: str, worksheet_name: str, token: str) -> list[dict[str, str]]:
    response = post_json(
        "/read_sheet",
        {"uri": uri, "worksheet_name": worksheet_name},
        token,
    )
    if not response.get("success"):
        raise RuntimeError(f"Failed to read worksheet: {worksheet_name}")
    return response.get("data", [])


def list_worksheets(uri: str, token: str) -> list[dict[str, Any]]:
    response = post_json("/list_worksheets", {"uri": uri}, token)
    return response.get("worksheets", [])


def write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def rows_to_matrix(rows: list[dict[str, Any]], headers: list[str]) -> list[list[str]]:
    matrix = [headers]
    for row in rows:
        values: list[str] = []
        for key in headers:
            value = row.get(key, "")
            if isinstance(value, float):
                if value.is_integer():
                    values.append(str(int(value)))
                else:
                    values.append(f"{value:.4f}".rstrip("0").rstrip("."))
            else:
                values.append(str(value))
        matrix.append(values)
    return matrix


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_money(value: float) -> str:
    return f"{value:,.2f}"


def fmt_pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"


def to_float(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    text = (
        text.replace(",", "")
        .replace("￥", "")
        .replace("%", "")
        .replace("，", "")
        .replace(" ", "")
    )
    try:
        return float(text)
    except ValueError:
        return 0.0


def to_ratio(value: Any) -> float:
    text = str(value).strip()
    if not text:
        return 0.0
    if text.endswith("%"):
        return to_float(text) / 100.0
    numeric = to_float(text)
    return numeric if numeric <= 1 else numeric / 100.0


def iso_day(text: str) -> str:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", str(text))
    return match.group(1) if match else ""


def month_of_day(day: str) -> str:
    return day[:7] if len(day) >= 7 else ""


@dataclass
class WorkbookData:
    monthly_trend: list[dict[str, str]]
    shop_summary: list[dict[str, str]]
    product_ranking: list[dict[str, str]]
    fulfillment: list[dict[str, str]]
    accounting: list[dict[str, str]]
    orders: list[dict[str, str]]
    refunds: list[dict[str, str]]
    shop_mapping: dict[str, str]
    worksheets: list[dict[str, Any]]


def load_workbook_data(uri: str, token: str) -> WorkbookData:
    worksheets_resp = post_json("/list_worksheets", {"uri": uri}, token)
    monthly_trend = read_sheet(uri, "汇总_月度趋势", token)
    shop_summary = read_sheet(uri, "汇总_按店铺", token)
    product_ranking = read_sheet(uri, "汇总_商品排名", token)
    fulfillment = read_sheet(uri, "履约率", token)
    accounting = read_sheet(uri, "核算表", token)
    orders = read_sheet(uri, "订单", token)
    refunds = read_sheet(uri, "退货订单表", token)
    shop_mapping_rows = read_sheet(uri, "店铺mapping", token)
    shop_mapping = {
        str(row.get("店铺ID", "")).strip(): str(row.get("店铺名字", "")).strip()
        for row in shop_mapping_rows
        if row.get("店铺ID")
    }
    return WorkbookData(
        monthly_trend=monthly_trend,
        shop_summary=shop_summary,
        product_ranking=product_ranking,
        fulfillment=fulfillment,
        accounting=accounting,
        orders=orders,
        refunds=refunds,
        shop_mapping=shop_mapping,
        worksheets=worksheets_resp.get("worksheets", []),
    )


def accounting_enriched_rows(data: WorkbookData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in data.accounting:
        day = iso_day(row.get("订单创建时间", ""))
        shop_id = str(row.get("店铺", "")).strip()
        rows.append(
            {
                "日期": day,
                "月份": month_of_day(day),
                "店铺ID": shop_id,
                "店铺": data.shop_mapping.get(shop_id, shop_id),
                "订单号": row.get("订单号", ""),
                "订单状态": row.get("订单状态", ""),
                "商品名称": row.get("商品名称", ""),
                "货号": row.get("货号", ""),
                "销售额(CNY)": to_float(row.get("销售额(CNY)", "")),
                "总成本(CNY)": to_float(row.get("总成本(CNY)", "")),
                "单品毛利(CNY)": to_float(row.get("单品毛利(CNY)", "")),
                "毛利率": to_ratio(row.get("毛利率", "")),
            }
        )
    return rows


def order_enriched_rows(data: WorkbookData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in data.orders:
        day = iso_day(row.get("Order Creation Date", ""))
        shop_id = str(row.get("店铺", "")).strip()
        qty = to_float(row.get("Quantity", ""))
        deal_price = to_float(row.get("Deal Price", ""))
        estimated_income = to_float(row.get("Estimated Income", ""))
        rows.append(
            {
                "日期": day,
                "月份": month_of_day(day),
                "店铺ID": shop_id,
                "店铺": data.shop_mapping.get(shop_id, shop_id),
                "订单号": row.get("Order ID", ""),
                "订单状态": row.get("Order Status", ""),
                "商品名称": row.get("Product Name", ""),
                "物流方案": row.get("Shipping Option", ""),
                "数量": qty,
                "成交额(JPY)": deal_price * qty,
                "预估收入(JPY)": estimated_income,
            }
        )
    return rows


def refund_enriched_rows(data: WorkbookData) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in data.refunds:
        shop_id = str(row.get("店铺", "")).strip()
        rows.append(
            {
                "日期": iso_day(row.get("订单创建时间", "")),
                "店铺ID": shop_id,
                "店铺": data.shop_mapping.get(shop_id, shop_id),
                "订单号": row.get("订单号", ""),
                "货号": row.get("货号", ""),
                "商品名称": row.get("商品名称", ""),
                "订单状态": row.get("订单状态", ""),
            }
        )
    return rows


def build_summary_tables(data: WorkbookData) -> dict[str, list[dict[str, Any]]]:
    accounting_rows = accounting_enriched_rows(data)
    order_rows = order_enriched_rows(data)
    refund_rows = refund_enriched_rows(data)

    overview = []
    total_visitors = sum(to_float(row.get("总访客")) for row in data.shop_summary)
    total_add_to_cart = sum(to_float(row.get("总加购")) for row in data.shop_summary)
    total_orders = sum(to_float(row.get("总下单量")) for row in data.shop_summary)
    total_confirms = sum(to_float(row.get("总确认量")) for row in data.shop_summary)
    total_revenue_cny = sum(row["销售额(CNY)"] for row in accounting_rows)
    total_cost_cny = sum(row["总成本(CNY)"] for row in accounting_rows)
    total_profit_cny = sum(row["单品毛利(CNY)"] for row in accounting_rows)
    avg_margin = (total_profit_cny / total_revenue_cny) if total_revenue_cny else 0.0
    avg_fulfillment = (
        sum(to_ratio(row.get("履约率")) for row in data.fulfillment if row.get("店铺"))
        / max(1, len([row for row in data.fulfillment if row.get("店铺")]))
    )
    total_refund_orders = len(refund_rows)
    total_distinct_orders = len({row["订单号"] for row in order_rows if row["订单号"]})
    overview.append(
        {
            "总访客": int(total_visitors),
            "总加购": int(total_add_to_cart),
            "总下单量": int(total_orders),
            "总确认量": int(total_confirms),
            "核算销售额CNY": round(total_revenue_cny, 2),
            "核算总成本CNY": round(total_cost_cny, 2),
            "核算毛利CNY": round(total_profit_cny, 2),
            "平均毛利率": round(avg_margin, 4),
            "平均履约率": round(avg_fulfillment, 4),
            "退款订单数": total_refund_orders,
            "订单表去重订单数": total_distinct_orders,
        }
    )

    daily_trend_map: dict[str, dict[str, Any]] = {}
    for row in accounting_rows:
        if not row["日期"]:
            continue
        day = row["日期"]
        bucket = daily_trend_map.setdefault(
            day,
            {
                "日期": day,
                "核算销售额CNY": 0.0,
                "核算毛利CNY": 0.0,
                "订单数": 0,
            },
        )
        bucket["核算销售额CNY"] += row["销售额(CNY)"]
        bucket["核算毛利CNY"] += row["单品毛利(CNY)"]
        bucket["订单数"] += 1
    daily_trend = sorted(daily_trend_map.values(), key=lambda item: item["日期"])
    for item in daily_trend:
        item["核算销售额CNY"] = round(item["核算销售额CNY"], 2)
        item["核算毛利CNY"] = round(item["核算毛利CNY"], 2)

    monthly_store_trend = []
    for row in data.monthly_trend:
        monthly_store_trend.append(
            {
                "月份": row.get("月份", ""),
                "店铺": row.get("店铺", ""),
                "访客": int(to_float(row.get("访客"))),
                "加购": int(to_float(row.get("加购"))),
                "下单量": int(to_float(row.get("下单量"))),
                "确认量": int(to_float(row.get("确认量"))),
            }
        )

    store_profit: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"店铺": "", "销售额CNY": 0.0, "总成本CNY": 0.0, "毛利CNY": 0.0, "订单数": 0}
    )
    for row in accounting_rows:
        shop = row["店铺"]
        bucket = store_profit[shop]
        bucket["店铺"] = shop
        bucket["销售额CNY"] += row["销售额(CNY)"]
        bucket["总成本CNY"] += row["总成本(CNY)"]
        bucket["毛利CNY"] += row["单品毛利(CNY)"]
        bucket["订单数"] += 1
    store_profit_rows = []
    for shop, bucket in store_profit.items():
        revenue = bucket["销售额CNY"]
        margin = bucket["毛利CNY"] / revenue if revenue else 0.0
        store_profit_rows.append(
            {
                "店铺": shop,
                "销售额CNY": round(bucket["销售额CNY"], 2),
                "总成本CNY": round(bucket["总成本CNY"], 2),
                "毛利CNY": round(bucket["毛利CNY"], 2),
                "毛利率": round(margin, 4),
                "订单数": bucket["订单数"],
            }
        )
    store_profit_rows.sort(key=lambda item: item["毛利CNY"], reverse=True)

    store_summary = []
    summary_by_shop = {str(row.get("店铺", "")).strip(): row for row in data.shop_summary}
    fulfillment_by_shop = {str(row.get("店铺", "")).strip(): row for row in data.fulfillment}
    for shop in sorted({row.get("店铺", "") for row in data.shop_summary if row.get("店铺")}):
        shop_row = summary_by_shop.get(shop, {})
        fulfill_row = fulfillment_by_shop.get(shop, {})
        traffic = to_float(shop_row.get("总访客"))
        add_to_cart = to_float(shop_row.get("总加购"))
        ordered = to_float(shop_row.get("总下单量"))
        confirmed = to_float(shop_row.get("总确认量"))
        store_summary.append(
            {
                "店铺": shop,
                "总访客": int(traffic),
                "总加购": int(add_to_cart),
                "总下单量": int(ordered),
                "总确认量": int(confirmed),
                "访客到加购转化率": round(add_to_cart / traffic if traffic else 0.0, 4),
                "加购到下单转化率": round(ordered / add_to_cart if add_to_cart else 0.0, 4),
                "下单到确认转化率": round(confirmed / ordered if ordered else 0.0, 4),
                "履约率": round(to_ratio(fulfill_row.get("履约率", "")), 4),
                "违约率": round(to_ratio(fulfill_row.get("违约率", "")), 4),
                "违约订单数": int(to_float(fulfill_row.get("违约订单数"))),
            }
        )

    top_products = []
    for row in data.product_ranking:
        top_products.append(
            {
                "商品": row.get("商品", ""),
                "店铺": row.get("店铺", ""),
                "访客": int(to_float(row.get("访客"))),
                "加购": int(to_float(row.get("加购"))),
                "下单量": int(to_float(row.get("下单量"))),
                "确认量": int(to_float(row.get("确认量"))),
            }
        )
    top_products.sort(key=lambda item: item["确认量"], reverse=True)
    top_products = top_products[:10]

    refund_by_sku: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"货号": "", "商品名称": "", "退款订单数": 0, "店铺": set()}
    )
    for row in refund_rows:
        key = row["货号"] or row["商品名称"] or row["订单号"]
        bucket = refund_by_sku[key]
        bucket["货号"] = row["货号"]
        bucket["商品名称"] = row["商品名称"]
        bucket["退款订单数"] += 1
        if row["店铺"]:
            bucket["店铺"].add(row["店铺"])
    refund_breakdown = []
    for bucket in refund_by_sku.values():
        refund_breakdown.append(
            {
                "货号": bucket["货号"],
                "商品名称": bucket["商品名称"],
                "退款订单数": bucket["退款订单数"],
                "涉及店铺": "、".join(sorted(bucket["店铺"])),
            }
        )
    refund_breakdown.sort(key=lambda item: item["退款订单数"], reverse=True)
    refund_breakdown = refund_breakdown[:10]

    validation_notes = [
        {
            "校验项": "店铺流量与转化汇总",
            "结果": "使用 汇总_按店铺 作为店铺结构口径",
            "说明": "该表仅覆盖 2026-03 至 2026-04 的访客/加购/下单/确认汇总，不与 5 月订单金额趋势强行拼接。"
        },
        {
            "校验项": "履约率口径",
            "结果": "使用 履约率 表作为履约风险补充",
            "说明": "统计时间为 2026-05-15 15:59:00，店2 履约率最低，为 93.75%。"
        },
        {
            "校验项": "利润口径",
            "结果": "使用 核算表 作为销售额、成本、毛利主口径",
            "说明": "核算表行数高于订单主表，说明含成本补充行；适合做利润分析。"
        },
        {
            "校验项": "广告金额口径",
            "结果": "未纳入主 KPI",
            "说明": "广告页聚合结果异常为空，本次不将广告 ROI 作为核心经营结论。"
        },
    ]

    dashboard_summary = [
        {"指标": "总访客", "数值": int(total_visitors), "口径": "汇总_按店铺"},
        {"指标": "总加购", "数值": int(total_add_to_cart), "口径": "汇总_按店铺"},
        {"指标": "总下单量", "数值": int(total_orders), "口径": "汇总_按店铺"},
        {"指标": "总确认量", "数值": int(total_confirms), "口径": "汇总_按店铺"},
        {"指标": "毛利CNY", "数值": round(total_profit_cny, 2), "口径": "核算表"},
        {"指标": "平均履约率", "数值": round(avg_fulfillment, 4), "口径": "履约率"},
    ]

    return {
        "overview": overview,
        "daily_trend": daily_trend,
        "monthly_store_trend": monthly_store_trend,
        "store_summary": store_summary,
        "store_profit": store_profit_rows,
        "top_products": top_products,
        "refund_breakdown": refund_breakdown,
        "validation_notes": validation_notes,
        "dashboard_summary": dashboard_summary,
    }


def write_local_outputs(
    out_dir: Path,
    tables: dict[str, list[dict[str, Any]]],
    data: WorkbookData,
) -> None:
    write_csv(
        out_dir / "overview.csv",
        tables["overview"],
        [
            "总访客",
            "总加购",
            "总下单量",
            "总确认量",
            "核算销售额CNY",
            "核算总成本CNY",
            "核算毛利CNY",
            "平均毛利率",
            "平均履约率",
            "退款订单数",
            "订单表去重订单数",
        ],
    )
    write_csv(
        out_dir / "daily_trend.csv",
        tables["daily_trend"],
        ["日期", "核算销售额CNY", "核算毛利CNY", "订单数"],
    )
    write_csv(
        out_dir / "monthly_store_trend.csv",
        tables["monthly_store_trend"],
        ["月份", "店铺", "访客", "加购", "下单量", "确认量"],
    )
    write_csv(
        out_dir / "store_summary.csv",
        tables["store_summary"],
        [
            "店铺",
            "总访客",
            "总加购",
            "总下单量",
            "总确认量",
            "访客到加购转化率",
            "加购到下单转化率",
            "下单到确认转化率",
            "履约率",
            "违约率",
            "违约订单数",
        ],
    )
    write_csv(
        out_dir / "store_profit.csv",
        tables["store_profit"],
        ["店铺", "销售额CNY", "总成本CNY", "毛利CNY", "毛利率", "订单数"],
    )
    write_csv(
        out_dir / "top_products.csv",
        tables["top_products"],
        ["商品", "店铺", "访客", "加购", "下单量", "确认量"],
    )
    write_csv(
        out_dir / "refund_breakdown.csv",
        tables["refund_breakdown"],
        ["货号", "商品名称", "退款订单数", "涉及店铺"],
    )
    write_csv(
        out_dir / "validation_notes.csv",
        tables["validation_notes"],
        ["校验项", "结果", "说明"],
    )
    write_csv(
        out_dir / "dashboard_summary.csv",
        tables["dashboard_summary"],
        ["指标", "数值", "口径"],
    )
    overview = tables["overview"][0]
    best_profit_shop = tables["store_profit"][0]
    worst_fulfillment = min(tables["store_summary"], key=lambda item: item["履约率"])
    top_product = tables["top_products"][0]
    peak_day = max(tables["daily_trend"], key=lambda item: item["核算销售额CNY"])
    report = f"""# Maybe Sheet 全 workbook BI 分析

## 数据范围
- 来源工作簿: `{WORKBOOK_URI}`
- 分析范围: 全 workbook 关键经营表，不限于单张订单明细
- 覆盖表: `汇总_按店铺`、`汇总_月度趋势`、`汇总_商品排名`、`履约率`、`核算表`、`订单`、`退货订单表`、`店铺mapping`
- 工作表总数: {len(data.worksheets)}

## 核心结论
- 当前最强经营引擎是 `{best_profit_shop["店铺"]}`，贡献毛利 {fmt_money(best_profit_shop["毛利CNY"])} CNY，销售额 {fmt_money(best_profit_shop["销售额CNY"])} CNY。
- 利润峰值日出现在 `{peak_day["日期"]}`，当日核算销售额 {fmt_money(peak_day["核算销售额CNY"])} CNY，毛利 {fmt_money(peak_day["核算毛利CNY"])} CNY。
- 履约风险最高的是 `{worst_fulfillment["店铺"]}`，履约率 {fmt_pct(worst_fulfillment["履约率"])}，违约率 {fmt_pct(worst_fulfillment["违约率"])}。
- 头部商品为 `{top_product["商品"]}`，来自 `{top_product["店铺"]}`，确认量 {fmt_int(top_product["确认量"])}，具备显著拉动作用。

## 指标概览
- 总访客: {fmt_int(overview["总访客"])}
- 总加购: {fmt_int(overview["总加购"])}
- 总下单量: {fmt_int(overview["总下单量"])}
- 总确认量: {fmt_int(overview["总确认量"])}
- 核算销售额: {fmt_money(overview["核算销售额CNY"])} CNY
- 核算毛利: {fmt_money(overview["核算毛利CNY"])} CNY
- 平均毛利率: {fmt_pct(overview["平均毛利率"])}
- 平均履约率: {fmt_pct(overview["平均履约率"])}
- 退款订单数: {fmt_int(overview["退款订单数"])}

## 分析主线
- 店铺结构: 采用 `汇总_按店铺` 判断流量、加购、下单、确认的转化层级。
- 趋势变化: 采用 `汇总_月度趋势` 判断 2026-03 至 2026-04 的店铺增长结构，采用 `核算表` 重建 2026-05 的销售额与毛利日趋势。
- 利润表现: 采用 `核算表` 作为销售额、成本、毛利的主口径。
- 履约风险: 采用 `履约率` 判断各店铺违约与超时风险。
- 商品贡献: 采用 `汇总_商品排名` 判断商品级确认量集中度。
- 售后信号: 采用 `退货订单表` 判断退款货号与店铺分布。

## 口径说明
- `汇总_按店铺` 与 `汇总_月度趋势` 的时间范围以 2026-03 至 2026-04 为主，适合做经营结构与增长对比。
- `订单`、`核算表`、`履约率`、`退货订单表` 主要覆盖 2026-05 窗口，适合做近期经营质量判断。
- 因时间窗口不同，本次不将流量月度表与 5 月订单金额直接拼成同一条趋势线，而是分成“结构”和“近期经营”两套视角。
- `广告` 与 `商业分析` 金额字段当前不稳定，本次未纳入主 KPI。

## 产物说明
- 本地汇总表: `overview.csv`、`daily_trend.csv`、`monthly_store_trend.csv`、`store_summary.csv`、`store_profit.csv`、`top_products.csv`、`refund_breakdown.csv`
- Maybe Sheet 中间层: 将写入 `BI_*` worksheet，供后续 dashboard / infographic / PPT 自由复用
"""
    (out_dir / "report.md").write_text(report, encoding="utf-8")


def chart_layout(cell: str, from_col: int, from_row: int, to_col: int, to_row: int, width: int, height: int) -> dict[str, Any]:
    return {
        "cell": cell,
        "format": {
            "from": {"col": from_col, "row": from_row, "col_off": 0, "row_off": 0},
            "to": {"col": to_col, "row": to_row, "col_off": 0, "row_off": 0},
            "lock_aspect_ratio": True,
            "offset_x": 0,
            "offset_y": 0,
            "scale_x": 1,
            "scale_y": 1,
        },
        "width": width,
        "height": height,
    }


def ensure_unique_name(existing_names: set[str], preferred: str) -> str:
    if preferred not in existing_names:
        existing_names.add(preferred)
        return preferred
    suffix = 2
    while f"{preferred}_{suffix}" in existing_names:
        suffix += 1
    resolved = f"{preferred}_{suffix}"
    existing_names.add(resolved)
    return resolved


def delete_worksheet_by_gid(uri: str, gid: int, token: str) -> dict[str, Any]:
    return post_json("/delete_worksheet", {"uri": f"{uri}?gid={gid}"}, token)


def create_dashboard(uri: str, dashboard_name: str, token: str) -> dict[str, Any]:
    return post_json(
        "/write_new_worksheet",
        {"uri": uri, "worksheet_name": dashboard_name, "values": []},
        token,
    )


def write_matrix_worksheet(uri: str, worksheet_name: str, matrix: list[list[str]], token: str) -> dict[str, Any]:
    return post_json(
        "/write_new_worksheet",
        {
            "uri": uri,
            "worksheet_name": worksheet_name,
            "values": matrix,
        },
        token,
    )


def ensure_empty_worksheet(uri: str, worksheet_name: str, token: str) -> dict[str, Any]:
    return post_json(
        "/write_new_worksheet",
        {
            "uri": uri,
            "worksheet_name": worksheet_name,
            "values": [],
        },
        token,
    )


def pivot_upsert(uri: str, target_worksheet_name: str, anchor_cell: str, config: dict[str, Any], token: str) -> dict[str, Any]:
    return post_json(
        "/pivot_table/upsert",
        {
            "uri": uri,
            "target": {
                "worksheet_name": target_worksheet_name,
                "anchor_cell": anchor_cell,
            },
            "config": config,
            "skip_recalculation": True,
        },
        token,
    )


def sql_formula(sql: str) -> str:
    return '=SQL("' + sql.replace('"', '""') + '")'


def formula_set(uri: str, worksheet_name: str, cell: str, formula: str, token: str) -> dict[str, Any]:
    return post_json(
        "/formula/set",
        {
            "uri": uri,
            "worksheet_name": worksheet_name,
            "cell": cell,
            "formula": formula,
        },
        token,
    )


def export_intermediate_products_to_maybe(
    uri: str,
    tables: dict[str, list[dict[str, Any]]],
    data: WorkbookData,
    industry_style: dict[str, Any] | None,
    style_config: dict[str, Any] | None,
    token: str,
    existing_names: set[str],
    *,
    include_pivot_support: bool = False,
) -> dict[str, Any]:
    resolved_names: dict[str, str] = {}
    formula_specs = [
        (
            "overview",
            "BI_概览数据",
            'select sum(cast("总访客" as real)) as "总访客", sum(cast("总加购" as real)) as "总加购", sum(cast("总下单量" as real)) as "总下单量", sum(cast("总确认量" as real)) as "总确认量", round((select sum(cast("销售额(CNY)" as real)) from "核算表" where trim(cast("店铺" as text)) != ""), 2) as "核算销售额CNY", round((select sum(cast("总成本(CNY)" as real)) from "核算表" where trim(cast("店铺" as text)) != ""), 2) as "核算总成本CNY", round((select sum(cast("单品毛利(CNY)" as real)) from "核算表" where trim(cast("店铺" as text)) != ""), 2) as "核算毛利CNY", round((select sum(cast("单品毛利(CNY)" as real)) / nullif(sum(cast("销售额(CNY)" as real)), 0) from "核算表" where trim(cast("店铺" as text)) != ""), 4) as "平均毛利率", round((select avg(cast(replace("履约率", "%", "") as real) / 100.0) from "履约率" where trim("店铺") != ""), 4) as "平均履约率", (select count(*) from "退货订单表") as "退款订单数", (select count(distinct "Order ID") from "订单" where trim(coalesce("Order ID", "")) != "") as "订单表去重订单数" from "汇总_按店铺"',
        ),
        (
            "store_summary",
            "BI_店铺结构",
            'select s."店铺", cast(s."总访客" as real) as "总访客", cast(s."总加购" as real) as "总加购", cast(s."总下单量" as real) as "总下单量", cast(s."总确认量" as real) as "总确认量", round(cast(s."总加购" as real) / nullif(cast(s."总访客" as real), 0), 4) as "访客到加购转化率", round(cast(s."总下单量" as real) / nullif(cast(s."总加购" as real), 0), 4) as "加购到下单转化率", round(cast(s."总确认量" as real) / nullif(cast(s."总下单量" as real), 0), 4) as "下单到确认转化率", cast(replace(f."履约率", "%", "") as real) / 100.0 as "履约率", cast(replace(f."违约率", "%", "") as real) / 100.0 as "违约率", cast(f."违约订单数" as real) as "违约订单数" from "汇总_按店铺" s left join "履约率" f on s."店铺" = f."店铺" where trim(s."店铺") != "" order by cast(s."总确认量" as real) desc',
        ),
        (
            "store_profit",
            "BI_店铺利润",
            'select case cast("店铺" as text) when "5958119" then "店1" when "6257123" then "店2" when "11499497" then "店3" else cast("店铺" as text) end as "店铺", round(sum(cast("销售额(CNY)" as real)), 2) as "销售额CNY", round(sum(cast("总成本(CNY)" as real)), 2) as "总成本CNY", round(sum(cast("单品毛利(CNY)" as real)), 2) as "毛利CNY", round(sum(cast("单品毛利(CNY)" as real)) / nullif(sum(cast("销售额(CNY)" as real)), 0), 4) as "毛利率", count(*) as "订单数" from "核算表" where trim(cast("店铺" as text)) != "" group by 1 order by "毛利CNY" desc',
        ),
        (
            "top_products",
            "BI_商品Top10",
            'select "商品", "店铺", cast("访客" as real) as "访客", cast("加购" as real) as "加购", cast("下单量" as real) as "下单量", cast("确认量" as real) as "确认量" from "汇总_商品排名" order by cast("确认量" as real) desc limit 10',
        ),
        (
            "daily_trend",
            "BI_日趋势SQL",
            'select substr("订单创建时间", 1, 10) as "日期", round(sum(cast("销售额(CNY)" as real)), 2) as "核算销售额CNY", round(sum(cast("单品毛利(CNY)" as real)), 2) as "核算毛利CNY", count(*) as "订单数" from "核算表" where trim(cast("店铺" as text)) != "" group by 1 order by 1',
        ),
        (
            "monthly_store_trend",
            "BI_月度趋势SQL",
            'select "月份", "店铺", cast("访客" as real) as "访客", cast("加购" as real) as "加购", cast("下单量" as real) as "下单量", cast("确认量" as real) as "确认量" from "汇总_月度趋势" order by "月份", "店铺"',
        ),
        (
            "fulfillment",
            "BI_履约风险SQL",
            'select "店铺", "当前统计时间", cast("订单数" as real) as "订单数", cast("违约订单数" as real) as "违约订单数", cast(replace("违约率", "%", "") as real) / 100.0 as "违约率", cast(replace("履约率", "%", "") as real) / 100.0 as "履约率" from "履约率" where trim("店铺") != "" order by "履约率" asc',
        ),
        (
            "product_detail",
            "BI_商品明细SQL",
            'select "商品", "店铺", cast("访客" as real) as "访客", cast("加购" as real) as "加购", cast("下单量" as real) as "下单量", cast("确认量" as real) as "确认量" from "汇总_商品排名" order by cast("确认量" as real) desc',
        ),
        (
            "refund_breakdown",
            "BI_退款分析",
            'select coalesce("货号", "") as "货号", coalesce("商品名称", "") as "商品名称", count(*) as "退款订单数", replace(group_concat(distinct case cast("店铺" as text) when "5958119" then "店1" when "6257123" then "店2" when "11499497" then "店3" else cast("店铺" as text) end), ",", "、") as "涉及店铺" from "退货订单表" group by 1, 2 order by "退款订单数" desc limit 10',
        ),
        (
            "validation_notes",
            "BI_校验说明",
            "select '店铺流量与转化汇总' as \"校验项\", '使用 汇总_按店铺 作为店铺结构口径' as \"结果\", '该表仅覆盖 2026-03 至 2026-04 的访客、加购、下单、确认汇总，不与 5 月订单金额趋势强行拼接。' as \"说明\" union all select '履约率口径' as \"校验项\", '使用 履约率 表作为履约风险补充' as \"结果\", '统计时间为 2026-05-15 15:59:00，店2 履约率最低，为 93.75%。' as \"说明\" union all select '利润口径' as \"校验项\", '使用 核算表 作为销售额、成本、毛利主口径' as \"结果\", '核算表行数高于订单主表，说明含成本补充行；适合做利润分析。' as \"说明\" union all select '广告金额口径' as \"校验项\", '未纳入主 KPI' as \"结果\", '广告页聚合结果异常为空，本次不将广告 ROI 作为核心经营结论。' as \"说明\"",
        ),
    ]

    formula_results = []
    formula_readbacks = {}
    for key, preferred_name, sql in formula_specs:
        resolved_name = ensure_unique_name(existing_names, preferred_name)
        resolved_names[key] = resolved_name
        ensure_empty_worksheet(uri, resolved_name, token)
        formula = sql_formula(sql)
        formula_results.append(
            formula_set(
                uri,
                resolved_name,
                "A1",
                formula,
                token,
            )
        )
        readback = post_json("/read_sheet", {"uri": uri, "worksheet_name": resolved_name}, token)
        formulas = readback.get("formulas") or []
        formula_readbacks[resolved_name] = {
            "shape": readback.get("shape"),
            "headers": readback.get("headers"),
            "formula_a1": formulas[0][0] if formulas and formulas[0] else None,
        }

    style_sheet_name = None
    style_write_result = None
    style_sheet_readback = None
    if industry_style is not None and style_config is not None:
        style_sheet_name = ensure_unique_name(existing_names, "BI_StyleConfig")
        style_matrix = style_config_to_matrix(industry_style, style_config)
        style_write_result = write_matrix_worksheet(uri, style_sheet_name, style_matrix, token)
        style_sheet_readback = post_json("/read_sheet", {"uri": uri, "worksheet_name": style_sheet_name}, token)
        resolved_names["style_config"] = style_sheet_name

    pivot_name = None
    pivot_results: list[dict[str, Any]] = []
    pivot_readback: dict[str, Any] | None = None
    if include_pivot_support:
        pivot_name = ensure_unique_name(existing_names, "BI_中间透视")
        ensure_empty_worksheet(uri, pivot_name, token)
        pivot_results.append(
            pivot_upsert(
                uri,
                pivot_name,
                "A1",
                {
                    "worksheet_gid": 50,
                    "worksheet_name": "汇总_按店铺",
                    "range_address": "A1:E4",
                    "row_fields": ["店铺"],
                    "metrics": [{"aggregate": "sum", "value_field": "总确认量", "label": "总确认量"}],
                    "show_row_totals": True,
                    "show_column_totals": True,
                    "blank_label": "(blank)",
                },
                token,
            )
        )
        pivot_results.append(
            pivot_upsert(
                uri,
                pivot_name,
                "E1",
                {
                    "worksheet_gid": 51,
                    "worksheet_name": "汇总_月度趋势",
                    "range_address": "A1:F7",
                    "row_fields": ["月份"],
                    "column_fields": ["店铺"],
                    "metrics": [{"aggregate": "sum", "value_field": "确认量", "label": "确认量"}],
                    "show_row_totals": True,
                    "show_column_totals": True,
                    "blank_label": "(blank)",
                },
                token,
            )
        )
        pivot_results.append(
            pivot_upsert(
                uri,
                pivot_name,
                "K1",
                {
                    "worksheet_gid": 52,
                    "worksheet_name": "汇总_商品排名",
                    "range_address": "A1:F21",
                    "row_fields": ["店铺"],
                    "column_fields": ["商品"],
                    "metrics": [{"aggregate": "sum", "value_field": "确认量", "label": "确认量"}],
                    "show_row_totals": True,
                    "show_column_totals": True,
                    "blank_label": "(blank)",
                },
                token,
            )
        )
        resolved_names["pivot"] = pivot_name
        pivot_sheet_readback = post_json("/read_sheet", {"uri": uri, "worksheet_name": pivot_name}, token)
        pivot_readback = {
            "shape": pivot_sheet_readback.get("shape"),
            "headers": pivot_sheet_readback.get("headers"),
            "values": pivot_sheet_readback.get("values", [])[:12],
        }

    return {
        "resolved_names": resolved_names,
        "intermediate_priority": ["sql_formula", "pivot", "static_fallback"],
        "sql_formula_first": True,
        "sql_formula_source_policy": "direct_from_raw_tables",
        "pivot_enabled": include_pivot_support,
        "pivot_worksheet_name": pivot_name,
        "pivot_results": pivot_results,
        "formula_results": formula_results,
        "formula_readbacks": formula_readbacks,
        "style_sheet_name": style_sheet_name,
        "style_write_result": style_write_result,
        "style_readback": (
            {
                "shape": style_sheet_readback.get("shape"),
                "headers": style_sheet_readback.get("headers"),
                "values": style_sheet_readback.get("values", [])[:20],
            }
            if style_sheet_readback
            else None
        ),
        "pivot_readback": pivot_readback,
    }


def cleanup_bi_worksheets(uri: str, token: str) -> list[dict[str, Any]]:
    worksheets = list_worksheets(uri, token)
    delete_titles = {
        "BI_Dashboard",
        "BI_中间透视",
        "BI_中间透视_2",
        "BI_中间透视_3",
        "BI_概览数据",
        "BI_日趋势",
        "BI_月度店铺趋势",
        "BI_店铺结构",
        "BI_店铺利润",
        "BI_商品Top10",
        "BI_退款分析",
        "BI_校验说明",
        "BI_SQL_Test",
        "BI_SQL_结果",
        "BI_日趋势SQL",
        "BI_月度趋势SQL",
        "BI_履约风险SQL",
        "BI_商品明细SQL",
        "BI_StyleConfig",
        "经营总览Dashboard",
        "经营总览Dashboard_2",
        "经营总览Dashboard_3",
    }
    deleted = []
    for worksheet in worksheets:
        title = str(worksheet.get("title", "")).strip()
        gid = worksheet.get("sheet_id")
        if title in delete_titles and gid is not None:
            deleted.append(delete_worksheet_by_gid(uri, int(gid), token))
    return deleted


def sql_write_result(uri: str, dashboard_name: str, start_cell: str, sql: str, token: str) -> dict[str, Any]:
    return post_json(
        "/sql/write_result",
        {
            "uri": uri,
            "sql": sql,
            "target_worksheet_name": dashboard_name,
            "target_start_cell": start_cell,
            "create_sheet_if_missing": False,
            "clear_target_range": True,
            "include_headers": True,
        },
        token,
    )


def add_chart(uri: str, dashboard_name: str, chart: dict[str, Any], token: str) -> dict[str, Any]:
    payload = {
        "uri": uri,
        "worksheet_name": dashboard_name,
        "cell": chart["cell"],
        "chart": {
            "type": "json",
            "title": chart["title"],
            "width": chart["width"],
            "height": chart["height"],
            "sql": chart["sql"],
            "spec": chart["spec"],
            "html": chart["html"],
            "series": [],
            "legend": chart.get("legend", "bottom"),
            "show_blanks": "gap",
            "x_axis_name": chart.get("x_axis_name", ""),
            "y_axis_name": chart.get("y_axis_name", ""),
            "format": chart["format"],
        },
    }
    return post_json("/add_chart", payload, token)


def build_dashboard_plan(dashboard_name: str, style_config: dict[str, Any]) -> dict[str, Any]:
    dashboard_style = style_config["dashboard"]["chart_style_defaults"]
    chart_theme = {
        "background": dashboard_style["background"],
        "titleColor": dashboard_style["titleColor"],
        "textColor": dashboard_style["textColor"],
        "subTextColor": dashboard_style["subTextColor"],
        "axisColor": dashboard_style["axisColor"],
        "gridLineColor": dashboard_style["gridLineColor"],
        "legendTextColor": dashboard_style["legendTextColor"],
        "tooltipBackground": dashboard_style["tooltipBackground"],
        "tooltipTextColor": dashboard_style["tooltipTextColor"],
        "fontFamily": "PingFang SC, Noto Sans SC, sans-serif",
    }
    palette = dashboard_style["palette"]
    return {
        "dashboard_worksheet_name": dashboard_name,
        "industry_style": style_config["industry_style"],
        "style_variant": style_config["dashboard"]["style_variant"],
        "charts": [
            {
                "goal": "看 2026-03 至 2026-04 各店铺确认量变化",
                "source_worksheet": "BI_月度趋势SQL",
                "dimension": "月份",
                "grouping_dimension": "店铺",
                "metric": "确认量",
                "chart_type": "json",
                "title": "店铺月度确认量趋势",
                "sql": 'select "月份", "店铺", "确认量" from "BI_月度趋势SQL" order by "月份", "店铺"',
                "spec": {"style": {"title": "店铺月度确认量趋势", "smooth": True, "legend": "bottom", "palette": palette[:3], **chart_theme}, "boxAdaptation": {"showDataZoom": "auto"}},
                "html": "{ library: 'echarts', handler: (data) => { const months = Array.from(new Set(data.map(item => item['月份']))); const stores = Array.from(new Set(data.map(item => item['店铺']))); return { tooltip: { trigger: 'axis' }, legend: { bottom: 8, textStyle: { fontSize: 14 } }, grid: { left: 56, right: 24, top: 36, bottom: 58 }, xAxis: { type: 'category', axisLabel: { fontSize: 14 }, data: months }, yAxis: { type: 'value', name: '确认量', nameTextStyle: { fontSize: 14 }, axisLabel: { fontSize: 13 } }, series: stores.map((store) => ({ name: store, type: 'line', smooth: true, symbolSize: 10, lineStyle: { width: 4 }, data: months.map((month) => { const row = data.find(item => item['月份'] === month && item['店铺'] === store); return row ? (Number(row['确认量']) || 0) : 0; }) })) }; } }",
                "layout": chart_layout("B2", 1, 1, 14, 13, 1313, 324),
                "x_axis_name": "月份",
                "y_axis_name": "确认量",
            },
            {
                "goal": "看店铺流量与转化规模差异",
                "source_worksheet": "BI_店铺结构",
                "dimension": "店铺",
                "grouping_dimension": None,
                "metric": "总访客/总加购/总下单量/总确认量",
                "chart_type": "json",
                "title": "店铺流量与转化结构",
                "sql": 'select "店铺", "总访客", "总加购", "总下单量", "总确认量" from "BI_店铺结构" order by "总确认量" desc',
                "spec": {"style": {"title": "店铺流量与转化结构", "legend": "bottom", "palette": [palette[0], palette[3], palette[2], palette[1]], **chart_theme}, "boxAdaptation": {"showDataZoom": "auto"}},
                "html": "{ library: 'echarts', handler: (data) => ({ tooltip: { trigger: 'axis' }, legend: { bottom: 8, textStyle: { fontSize: 13 } }, grid: { left: 56, right: 20, top: 36, bottom: 58 }, xAxis: { type: 'category', axisLabel: { fontSize: 14 }, data: data.map(item => item['店铺']) }, yAxis: { type: 'value', axisLabel: { fontSize: 13 } }, series: ['总访客','总加购','总下单量','总确认量'].map((key) => ({ name: key, type: 'bar', barMaxWidth: 28, data: data.map(item => Number(item[key]) || 0) })) }) }",
                "layout": chart_layout("B15", 1, 14, 7, 24, 606, 270),
                "x_axis_name": "店铺",
                "y_axis_name": "数量",
            },
            {
                "goal": "看店铺履约风险高低",
                "source_worksheet": "BI_履约风险SQL",
                "dimension": "店铺",
                "grouping_dimension": None,
                "metric": "履约率/违约率",
                "chart_type": "json",
                "title": "店铺履约风险对比",
                "sql": 'select "店铺", "履约率", "违约率", "违约订单数" from "BI_履约风险SQL" order by "履约率" asc',
                "spec": {"style": {"title": "店铺履约风险对比", "legend": "bottom", "palette": [palette[3], palette[4]], **chart_theme}, "boxAdaptation": {"showDataZoom": "auto"}},
                "html": "{ library: 'echarts', handler: (data) => ({ tooltip: { trigger: 'axis', valueFormatter: (value) => `${(Number(value || 0) * 100).toFixed(2)}%` }, legend: { bottom: 8, textStyle: { fontSize: 13 } }, grid: { left: 56, right: 20, top: 36, bottom: 58 }, xAxis: { type: 'category', axisLabel: { fontSize: 14 }, data: data.map(item => item['店铺']) }, yAxis: { type: 'value', min: 0, max: 1, axisLabel: { fontSize: 13, formatter: (value) => `${Math.round(value * 100)}%` } }, series: [{ name: '履约率', type: 'bar', barMaxWidth: 32, data: data.map(item => Number(item['履约率']) || 0) }, { name: '违约率', type: 'bar', barMaxWidth: 32, data: data.map(item => Number(item['违约率']) || 0) }] }) }",
                "layout": chart_layout("H15", 7, 14, 13, 24, 606, 270),
                "x_axis_name": "店铺",
                "y_axis_name": "比率",
            },
            {
                "goal": "看店铺利润规模与毛利率差异",
                "source_worksheet": "BI_店铺利润",
                "dimension": "店铺",
                "grouping_dimension": None,
                "metric": "毛利CNY/毛利率",
                "chart_type": "json",
                "title": "店铺毛利与毛利率",
                "sql": 'select "店铺", "销售额CNY", "毛利CNY", "毛利率" from "BI_店铺利润" order by "毛利CNY" desc',
                "spec": {"style": {"title": "店铺毛利与毛利率", "legend": "bottom", "palette": [palette[2], palette[0]], **chart_theme}, "boxAdaptation": {"showDataZoom": "auto"}},
                "html": "{ library: 'echarts', handler: (data) => ({ tooltip: { trigger: 'axis' }, legend: { bottom: 8, textStyle: { fontSize: 13 } }, grid: { left: 56, right: 44, top: 36, bottom: 58 }, xAxis: { type: 'category', axisLabel: { fontSize: 14 }, data: data.map(item => item['店铺']) }, yAxis: [{ type: 'value', name: '毛利CNY', axisLabel: { fontSize: 13 } }, { type: 'value', name: '毛利率', min: 0, max: 0.6, axisLabel: { fontSize: 13, formatter: (value) => `${Math.round(value * 100)}%` } }], series: [{ name: '毛利CNY', type: 'bar', barMaxWidth: 36, data: data.map(item => Number(item['毛利CNY']) || 0) }, { name: '毛利率', type: 'line', yAxisIndex: 1, smooth: true, symbolSize: 10, lineStyle: { width: 4 }, data: data.map(item => Number(item['毛利率']) || 0) }] }) }",
                "layout": chart_layout("B26", 1, 25, 14, 37, 1313, 324),
                "x_axis_name": "店铺",
                "y_axis_name": "毛利",
            },
            {
                "goal": "看头部商品确认量集中度",
                "source_worksheet": "BI_商品Top10",
                "dimension": "商品",
                "grouping_dimension": "店铺",
                "metric": "确认量",
                "chart_type": "json",
                "title": "核心商品确认量Top10",
                "sql": 'select "商品", "店铺", "确认量" from "BI_商品Top10" order by "确认量" desc',
                "spec": {"style": {"title": "核心商品确认量Top10", "palette": [palette[0]], **chart_theme}, "boxAdaptation": {"showDataZoom": "auto"}},
                "html": "{ library: 'echarts', handler: (data) => ({ tooltip: { trigger: 'axis' }, grid: { left: 210, right: 28, top: 36, bottom: 32 }, xAxis: { type: 'value', axisLabel: { fontSize: 13 } }, yAxis: { type: 'category', axisLabel: { fontSize: 14, width: 180, overflow: 'truncate' }, data: data.map(item => `${item['店铺']} | ${String(item['商品']).slice(0, 18)}`).reverse() }, series: [{ type: 'bar', barMaxWidth: 24, itemStyle: { borderRadius: [0, 6, 6, 0] }, label: { show: true, position: 'right', fontSize: 13 }, data: data.map(item => Number(item['确认量']) || 0).reverse() }] }) }",
                "layout": chart_layout("B39", 1, 38, 14, 50, 1313, 324),
                "x_axis_name": "确认量",
                "y_axis_name": "商品",
            },
        ],
    }


def write_dashboard(uri: str, dashboard_name: str, style_config: dict[str, Any], token: str) -> dict[str, Any]:
    create_result = create_dashboard(uri, dashboard_name, token)
    plan = build_dashboard_plan(dashboard_name, style_config)
    chart_results = []
    for chart in plan["charts"]:
        payload = {
            "title": chart["title"],
            "sql": chart["sql"],
            "spec": chart["spec"],
            "html": chart["html"],
            "cell": chart["layout"]["cell"],
            "format": chart["layout"]["format"],
            "width": chart["layout"]["width"],
            "height": chart["layout"]["height"],
            "legend": chart.get("legend", "bottom"),
            "x_axis_name": chart.get("x_axis_name", ""),
            "y_axis_name": chart.get("y_axis_name", ""),
        }
        chart_results.append(add_chart(uri, dashboard_name, payload, token))
    charts_resp = post_json("/get_charts", {"uri": uri, "worksheet_name": dashboard_name}, token)
    return {
        "create_result": create_result,
        "chart_results": chart_results,
        "get_charts": charts_resp,
        "plan": plan,
    }


def run_layout_validator(uri: str, dashboard_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "rtk",
            "node",
            "/Users/duke/.codex/skills/sheet-dashboard/scripts/validate_dashboard_layout.mjs",
            "--uri",
            uri,
            "--worksheet",
            dashboard_name,
            "--fix-reset-layout",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def render_infographic(out_dir: Path, presentation_payload: dict[str, Any]) -> dict[str, Any]:
    payload_path = out_dir / "presentation-payload.json"
    if not payload_path.exists():
        payload_path.write_text(json.dumps(presentation_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    completed = subprocess.run(
        [
            "python3",
            str(INFOGRAPHIC_RENDER_SCRIPT),
            "--presentation-payload",
            str(payload_path),
            "--output-dir",
            str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run whole-workbook BI analysis for a Maybe Sheet workbook.")
    parser.add_argument("--uri", default=WORKBOOK_URI)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dashboard-name", default=DEFAULT_DASHBOARD_NAME)
    parser.add_argument("--with-style", action="store_true", help="Generate style-config.json and presentation-payload.json.")
    parser.add_argument("--with-dashboard", action="store_true", help="Generate dashboard artifacts and write dashboard worksheet.")
    parser.add_argument("--with-infographic", action="store_true", help="Generate infographic artifacts. Implies --with-style.")
    parser.add_argument("--skip-layout-validator", action="store_true")
    parser.add_argument("--skip-infographic", action="store_true")
    args = parser.parse_args()

    token = get_token()
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    deleted_worksheets = cleanup_bi_worksheets(args.uri, token)
    data = load_workbook_data(args.uri, token)
    existing_names = {str(item.get("title", "")).strip() for item in data.worksheets}
    dashboard_name = args.dashboard_name
    existing_names.add(dashboard_name)
    tables = build_summary_tables(data)
    write_local_outputs(out_dir, tables, data)

    style_enabled = args.with_style or args.with_dashboard or args.with_infographic
    infographic_enabled = args.with_infographic and not args.skip_infographic

    industry_style = None
    style_config = None
    presentation_payload = None
    if style_enabled:
        industry_style = infer_industry_style(tables, data)
        style_config = build_style_config(industry_style)
        (out_dir / "style-config.json").write_text(
            json.dumps(style_config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        presentation_payload = build_presentation_payload(tables, industry_style, style_config)
        (out_dir / "presentation-payload.json").write_text(
            json.dumps(presentation_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    intermediate_export = export_intermediate_products_to_maybe(
        args.uri,
        tables,
        data,
        industry_style,
        style_config,
        token,
        existing_names,
        include_pivot_support=False,
    )

    dashboard_result = None
    if args.with_dashboard:
        if style_config is None:
            raise SystemExit("--with-dashboard requires style config")
        dashboard_result = write_dashboard(args.uri, dashboard_name, style_config, token)
    validator = None
    if args.with_dashboard and not args.skip_layout_validator:
        validator = run_layout_validator(args.uri, dashboard_name)
    refreshed_worksheets = post_json("/list_worksheets", {"uri": args.uri}, token).get("worksheets", [])
    dashboard_gid = None
    if args.with_dashboard:
        for worksheet in refreshed_worksheets:
            if str(worksheet.get("title", "")).strip() == dashboard_name:
                dashboard_gid = worksheet.get("sheet_id")
                break
    infographic_result = None
    if infographic_enabled:
        if industry_style is None or style_config is None or presentation_payload is None:
            raise SystemExit("--with-infographic requires style config")
        infographic_result = render_infographic(out_dir, presentation_payload)

    result = {
        "success": True,
        "workbook_uri": args.uri,
        "output_dir": str(out_dir),
        "industry_style": industry_style,
        "style_config_path": str(out_dir / "style-config.json") if style_config else None,
        "style_config": style_config,
        "deleted_worksheets": deleted_worksheets,
        "dashboard_name": dashboard_name,
        "dashboard_url": (
            f"{args.uri}?gid={dashboard_gid}"
            if dashboard_gid is not None
            else (dashboard_result["create_result"].get("spreadsheet_url", "") if dashboard_result else "")
        ),
        "dashboard_gid": dashboard_gid,
        "intermediate_export": intermediate_export,
        "dashboard_create_result": dashboard_result["create_result"] if dashboard_result else None,
        "dashboard_chart_count": len(dashboard_result["get_charts"].get("charts", [])) if dashboard_result else 0,
        "dashboard_plan": dashboard_result["plan"] if dashboard_result else None,
        "layout_validator_exit_code": validator.returncode if validator else None,
        "layout_validator_stdout": validator.stdout if validator else "",
        "layout_validator_stderr": validator.stderr if validator else "",
        "infographic": infographic_result,
    }
    (out_dir / "run_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
