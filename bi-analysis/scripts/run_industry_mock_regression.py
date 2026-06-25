#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


SIZE_MAP = {
    "small": 1_000,
    "medium": 10_000,
    "large": 100_000,
}


@dataclass(frozen=True)
class IndustrySpec:
    key: str
    label: str
    fact_table: str
    grain: str
    time_col: str
    primary_metric: str
    dimensions: list[str]
    status_dimensions: list[str]
    hierarchies: list[str]
    dimension_packs: list[str]
    priority_cuts: list[str]
    preferred_size: str


SPECS: dict[str, IndustrySpec] = {
    "retail": IndustrySpec(
        key="retail",
        label="Retail / E-commerce",
        fact_table="orders",
        grain="one row per order line",
        time_col="order_date",
        primary_metric="gross_sales",
        dimensions=["region", "store_name", "category", "subcategory", "sku", "channel", "customer_segment"],
        status_dimensions=["order_status", "refund_status"],
        hierarchies=["month > week > day", "region > store_name", "category > subcategory > sku"],
        dimension_packs=["time", "geography", "product", "channel", "customer", "status"],
        priority_cuts=["time x gross_sales", "store_name x gross_sales", "sku x profit", "refund_status x refund_amount"],
        preferred_size="small",
    ),
    "saas": IndustrySpec(
        key="saas",
        label="SaaS / AI Usage",
        fact_table="usage_logs",
        grain="one row per usage event batch",
        time_col="event_date",
        primary_metric="revenue_usd",
        dimensions=["account_tier", "customer_industry", "plan_name", "provider", "model_family", "feature_module", "region"],
        status_dimensions=["request_status", "ticket_status"],
        hierarchies=["month > week > day", "plan_name > account_tier > account_name", "provider > model_family > model_name"],
        dimension_packs=["time", "customer", "product", "channel", "organization", "status"],
        priority_cuts=["time x revenue_usd", "plan_name x margin_usd", "model_family x cost_usd", "request_status x request_count"],
        preferred_size="medium",
    ),
    "manufacturing": IndustrySpec(
        key="manufacturing",
        label="Manufacturing / Supply Chain",
        fact_table="production_orders",
        grain="one row per production order",
        time_col="production_date",
        primary_metric="output_units",
        dimensions=["plant", "line_name", "product_family", "product_name", "sku", "supplier", "warehouse_region", "shift_name"],
        status_dimensions=["order_status", "quality_status", "inventory_status"],
        hierarchies=["month > week > day", "plant > line_name", "product_family > product_name > sku"],
        dimension_packs=["time", "organization", "product", "inventory", "supply", "status", "risk"],
        priority_cuts=["time x output_units", "plant x defect_rate", "supplier x delay_minutes", "inventory_status x on_time_rate"],
        preferred_size="large",
    ),
    "marketplace": IndustrySpec(
        key="marketplace",
        label="Marketplace / O2O",
        fact_table="transactions",
        grain="one row per marketplace transaction",
        time_col="transaction_date",
        primary_metric="gmv_usd",
        dimensions=["city", "seller_tier", "category", "campaign_name", "buyer_segment", "service_mode", "merchant_type"],
        status_dimensions=["fulfillment_status", "complaint_status"],
        hierarchies=["month > week > day", "city > merchant_type > seller_name", "category > subcategory > sku"],
        dimension_packs=["time", "geography", "merchant", "product", "campaign", "customer", "status"],
        priority_cuts=["time x gmv_usd", "city x gmv_usd", "seller_tier x commission_usd", "complaint_status x complaint_cost_usd"],
        preferred_size="small",
    ),
    "finance": IndustrySpec(
        key="finance",
        label="Finance / Lending",
        fact_table="loans",
        grain="one row per loan contract",
        time_col="disbursement_date",
        primary_metric="disbursed_usd",
        dimensions=["channel", "customer_segment", "product_name", "region", "risk_grade", "branch_name", "term_bucket"],
        status_dimensions=["repayment_status", "overdue_status"],
        hierarchies=["month > week > day", "region > branch_name", "product_name > risk_grade > customer_segment"],
        dimension_packs=["time", "customer", "channel", "product", "organization", "status", "risk"],
        priority_cuts=["time x disbursed_usd", "channel x net_margin_usd", "risk_grade x overdue_amount_usd", "overdue_status x disbursed_usd"],
        preferred_size="medium",
    ),
    "logistics": IndustrySpec(
        key="logistics",
        label="Logistics / Delivery",
        fact_table="shipments",
        grain="one row per shipment order",
        time_col="shipment_date",
        primary_metric="delivery_revenue_usd",
        dimensions=["region", "station_name", "courier_type", "service_level", "route_type", "customer_segment", "carrier_name"],
        status_dimensions=["delivery_status", "claim_status"],
        hierarchies=["month > week > day", "region > station_name", "carrier_name > courier_type > service_level"],
        dimension_packs=["time", "geography", "organization", "service", "customer", "status", "risk"],
        priority_cuts=["time x delivery_revenue_usd", "region x on_time_flag", "carrier_name x late_minutes", "claim_status x claim_amount_usd"],
        preferred_size="small",
    ),
    "media": IndustrySpec(
        key="media",
        label="Media / Content / Community",
        fact_table="content_events",
        grain="one row per content-day aggregate event",
        time_col="event_date",
        primary_metric="ad_revenue_usd",
        dimensions=["content_type", "topic", "creator_tier", "distribution_channel", "user_segment", "region", "creator_name"],
        status_dimensions=["subscription_status", "moderation_status"],
        hierarchies=["month > week > day", "content_type > topic > creator_name", "distribution_channel > user_segment > region"],
        dimension_packs=["time", "content", "creator", "channel", "customer", "status"],
        priority_cuts=["time x ad_revenue_usd", "content_type x watch_minutes", "creator_tier x subscriptions", "subscription_status x ad_revenue_usd"],
        preferred_size="small",
    ),
    "healthcare": IndustrySpec(
        key="healthcare",
        label="Healthcare / Clinics",
        fact_table="appointments",
        grain="one row per patient visit",
        time_col="visit_date",
        primary_metric="billed_revenue_usd",
        dimensions=["hospital_region", "clinic_name", "department", "doctor_level", "payer_type", "service_line", "patient_segment"],
        status_dimensions=["visit_status", "followup_status"],
        hierarchies=["month > week > day", "hospital_region > clinic_name", "service_line > department > doctor_level"],
        dimension_packs=["time", "geography", "organization", "service", "customer", "status", "risk"],
        priority_cuts=["time x billed_revenue_usd", "department x margin_usd", "payer_type x billed_revenue_usd", "visit_status x no_show_count"],
        preferred_size="medium",
    ),
    "education": IndustrySpec(
        key="education",
        label="Education / Training",
        fact_table="learning_events",
        grain="one row per learner-course aggregate",
        time_col="learning_date",
        primary_metric="tuition_revenue_usd",
        dimensions=["program_type", "subject_area", "campus_region", "cohort_name", "acquisition_channel", "learner_segment", "instructor_tier"],
        status_dimensions=["enrollment_status", "completion_status"],
        hierarchies=["month > week > day", "program_type > subject_area > cohort_name", "campus_region > learner_segment > acquisition_channel"],
        dimension_packs=["time", "product", "geography", "channel", "customer", "status"],
        priority_cuts=["time x tuition_revenue_usd", "program_type x completion_rate", "acquisition_channel x tuition_revenue_usd", "completion_status x study_minutes"],
        preferred_size="small",
    ),
    "crypto": IndustrySpec(
        key="crypto",
        label="Crypto / Exchange Activity",
        fact_table="market_activity",
        grain="one row per market activity slice",
        time_col="block_date",
        primary_metric="traded_volume_usd",
        dimensions=["chain_name", "venue_type", "token_sector", "asset_symbol", "wallet_segment", "region", "trader_tier"],
        status_dimensions=["tx_status", "risk_status"],
        hierarchies=["month > week > day", "chain_name > venue_type > asset_symbol", "token_sector > asset_symbol > wallet_segment"],
        dimension_packs=["time", "product", "channel", "customer", "risk", "status"],
        priority_cuts=["time x traded_volume_usd", "chain_name x fee_revenue_usd", "asset_symbol x active_addresses", "risk_status x traded_volume_usd"],
        preferred_size="medium",
    ),
}


def fmt_int(value: float | int) -> str:
    return f"{int(round(float(value))):,}"


def fmt_money(value: float) -> str:
    return f"{float(value):,.2f}"


def fmt_pct(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_time_columns(frame: pd.DataFrame, col: str) -> pd.DataFrame:
    frame = frame.copy()
    dt = pd.to_datetime(frame[col])
    frame["month"] = dt.dt.to_period("M").astype(str)
    frame["week"] = dt.dt.to_period("W-SUN").astype(str)
    frame["day"] = dt.dt.strftime("%Y-%m-%d")
    return frame


def detect_measures(frame: pd.DataFrame, ignore: set[str]) -> list[str]:
    measures: list[str] = []
    for col in frame.columns:
        if col in ignore:
            continue
        if pd.api.types.is_numeric_dtype(frame[col]):
            measures.append(col)
    return measures


def choose_size(size_name: str) -> int:
    if size_name not in SIZE_MAP:
        raise ValueError(f"unsupported size: {size_name}")
    return SIZE_MAP[size_name]


def retail_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-01-01", periods=45, freq="D")
    regions = ["华东", "华南", "华北", "西南"]
    stores = {
        "华东": ["上海旗舰店", "杭州体验店"],
        "华南": ["深圳中心店", "广州天河店"],
        "华北": ["北京朝阳店", "天津滨海店"],
        "西南": ["成都高新店", "重庆观音桥店"],
    }
    categories = {
        "服饰": ["连衣裙", "衬衫", "牛仔裤"],
        "家居": ["床品", "收纳盒", "香薰"],
        "美妆": ["粉底液", "口红", "面膜"],
    }
    channels = ["自然流量", "直播", "搜索广告", "社媒投放"]
    segments = ["新客", "老客", "会员"]
    order_statuses = ["已支付", "已发货", "已完成", "已取消"]
    refund_statuses = ["无退款", "退款中", "已退款"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        day_idx = int(rng.integers(0, len(dates)))
        date = dates[day_idx]
        region = rng.choice(regions, p=[0.33, 0.25, 0.22, 0.20])
        store_name = rng.choice(stores[region])
        category = rng.choice(list(categories.keys()), p=[0.42, 0.28, 0.30])
        subcategory = rng.choice(categories[category])
        sku = f"{subcategory[:2]}-{rng.integers(100, 999)}"
        channel = rng.choice(channels, p=[0.30, 0.22, 0.28, 0.20])
        customer_segment = rng.choice(segments, p=[0.36, 0.44, 0.20])
        order_status = rng.choice(order_statuses, p=[0.12, 0.16, 0.62, 0.10])
        refund_status = rng.choice(refund_statuses, p=[0.84, 0.08, 0.08])
        base_units = max(1, int(rng.poisson(2.4) + 1))
        weekend_boost = 1.18 if date.weekday() >= 4 else 1.0
        promo_boost = 1.22 if channel in {"直播", "社媒投放"} else 1.0
        unit_price = {
            "服饰": 42.0,
            "家居": 29.0,
            "美妆": 21.0,
        }[category] * rng.uniform(0.82, 1.24)
        units = max(1, int(round(base_units * weekend_boost * promo_boost)))
        gross_sales = units * unit_price
        discount_rate = float(np.clip(rng.normal(0.10 if channel == "直播" else 0.06, 0.03), 0.0, 0.28))
        refund_ratio = 0.0 if refund_status == "无退款" else rng.uniform(0.2, 1.0)
        refund_amount = gross_sales * refund_ratio * (0.35 if refund_status == "退款中" else 0.8 if refund_status == "已退款" else 0.0)
        cogs = gross_sales * rng.uniform(0.48, 0.66)
        profit = gross_sales * (1 - discount_rate) - cogs - refund_amount
        rows_out.append(
            {
                "order_id": f"R{idx + 1:07d}",
                "order_date": date,
                "region": region,
                "store_name": store_name,
                "category": category,
                "subcategory": subcategory,
                "sku": sku,
                "channel": channel,
                "customer_segment": customer_segment,
                "order_status": order_status,
                "refund_status": refund_status,
                "units": units,
                "gross_sales": round(gross_sales, 2),
                "refund_amount": round(refund_amount, 2),
                "profit": round(profit, 2),
                "discount_rate": round(discount_rate, 4),
            }
        )

    orders = pd.DataFrame(rows_out)
    refunds = (
        orders.loc[orders["refund_status"] != "无退款", ["order_id", "order_date", "region", "store_name", "category", "refund_status", "refund_amount"]]
        .copy()
        .rename(columns={"order_date": "refund_date"})
    )
    traffic = (
        orders.groupby(["order_date", "channel", "region"], as_index=False)
        .agg(orders=("order_id", "count"), gross_sales=("gross_sales", "sum"))
        .assign(visits=lambda df: (df["orders"] * rng.integers(14, 30, size=len(df))).astype(int))
    )
    traffic["conversion_rate"] = (traffic["orders"] / traffic["visits"]).round(4)
    inventory = (
        orders.groupby(["category", "subcategory", "sku", "region"], as_index=False)
        .agg(sold_units=("units", "sum"))
        .assign(on_hand=lambda df: np.maximum(20, (df["sold_units"] * rng.uniform(0.8, 1.6, len(df))).astype(int)))
    )
    inventory["inventory_status"] = np.where(inventory["on_hand"] < inventory["sold_units"] * 0.9, "偏紧", "正常")
    return {"orders": orders, "refunds": refunds, "traffic": traffic, "inventory": inventory}


def saas_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-02-01", periods=60, freq="D")
    tiers = ["SMB", "Mid-Market", "Enterprise"]
    industries = ["零售", "教育", "金融", "制造", "游戏"]
    plans = ["Starter", "Growth", "Scale"]
    providers = {"OpenAI": ["gpt-4.1", "gpt-4o-mini"], "Anthropic": ["claude-3.7", "claude-3.5"], "DeepSeek": ["deepseek-chat", "deepseek-reasoner"]}
    features = ["文案生成", "图片生成", "知识问答", "自动工单", "数据洞察"]
    regions = ["中国", "东南亚", "欧洲"]
    statuses = ["success", "timeout", "error"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        account_tier = rng.choice(tiers, p=[0.46, 0.34, 0.20])
        plan_name = rng.choice(plans, p=[0.38, 0.40, 0.22])
        customer_industry = rng.choice(industries)
        provider = rng.choice(list(providers.keys()), p=[0.45, 0.32, 0.23])
        model_name = rng.choice(providers[provider])
        model_family = model_name.split("-")[0]
        feature_module = rng.choice(features, p=[0.24, 0.13, 0.20, 0.18, 0.25])
        region = rng.choice(regions, p=[0.58, 0.22, 0.20])
        request_status = rng.choice(statuses, p=[0.87, 0.06, 0.07])
        ticket_status = rng.choice(["open", "resolved", "sla_risk"], p=[0.09, 0.78, 0.13])
        request_count = max(1, int(rng.poisson(10 if plan_name == "Starter" else 18 if plan_name == "Growth" else 28)))
        tokens = int(request_count * rng.integers(900, 4200))
        image_requests = int(request_count * (0.25 if feature_module == "图片生成" else 0.05))
        cost_factor = {"OpenAI": 1.0, "Anthropic": 1.12, "DeepSeek": 0.62}[provider]
        plan_factor = {"Starter": 1.0, "Growth": 1.15, "Scale": 1.30}[plan_name]
        cost_usd = tokens / 1_000_000 * 2.2 * cost_factor + image_requests * 0.035
        revenue_usd = cost_usd * rng.uniform(1.55, 2.35) * plan_factor
        latency_seconds = max(0.8, float(rng.normal(4.8 if request_status == "success" else 9.5, 1.6)))
        rows_out.append(
            {
                "usage_id": f"S{idx + 1:07d}",
                "event_date": date,
                "account_name": f"acct_{rng.integers(1, max(15, rows // 40)):04d}",
                "account_tier": account_tier,
                "customer_industry": customer_industry,
                "plan_name": plan_name,
                "provider": provider,
                "model_family": model_family,
                "model_name": model_name,
                "feature_module": feature_module,
                "region": region,
                "request_status": request_status,
                "ticket_status": ticket_status,
                "request_count": request_count,
                "tokens": tokens,
                "image_requests": image_requests,
                "cost_usd": round(cost_usd, 4),
                "revenue_usd": round(revenue_usd, 4),
                "margin_usd": round(revenue_usd - cost_usd, 4),
                "latency_seconds": round(latency_seconds, 3),
            }
        )

    usage_logs = pd.DataFrame(rows_out)
    accounts = usage_logs[["account_name", "account_tier", "customer_industry", "plan_name", "region"]].drop_duplicates().reset_index(drop=True)
    plans = usage_logs.groupby("plan_name", as_index=False).agg(
        avg_requests=("request_count", "mean"),
        avg_tokens=("tokens", "mean"),
        revenue_usd=("revenue_usd", "sum"),
        margin_usd=("margin_usd", "sum"),
    )
    support_tickets = (
        usage_logs.groupby(["event_date", "account_tier", "ticket_status"], as_index=False)
        .agg(ticket_count=("usage_id", "count"), avg_latency=("latency_seconds", "mean"))
        .rename(columns={"event_date": "ticket_date"})
    )
    return {"usage_logs": usage_logs, "accounts": accounts, "plans": plans, "support_tickets": support_tickets}


def manufacturing_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-03-01", periods=75, freq="D")
    plants = {"华东工厂": ["涂装线", "总装线"], "华南工厂": ["组装线", "检测线"], "西部工厂": ["注塑线", "包装线"]}
    families = {"小家电": ["空气炸锅", "破壁机"], "智能设备": ["摄像头", "路由器"], "配件": ["滤芯", "支架"]}
    suppliers = ["星火供应", "远航材料", "晨曦电子", "蓝海组件"]
    shifts = ["白班", "中班", "夜班"]
    order_statuses = ["已完工", "生产中", "延迟"]
    quality_statuses = ["正常", "轻微缺陷", "严重缺陷"]
    inventory_statuses = ["健康", "偏紧", "积压"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        plant = rng.choice(list(plants.keys()), p=[0.40, 0.35, 0.25])
        line_name = rng.choice(plants[plant])
        product_family = rng.choice(list(families.keys()), p=[0.34, 0.38, 0.28])
        product_name = rng.choice(families[product_family])
        sku = f"{product_name[:2]}-{rng.integers(100, 999)}"
        supplier = rng.choice(suppliers)
        warehouse_region = rng.choice(["华东仓", "华南仓", "西南仓"], p=[0.45, 0.33, 0.22])
        shift_name = rng.choice(shifts, p=[0.45, 0.30, 0.25])
        order_status = rng.choice(order_statuses, p=[0.74, 0.18, 0.08])
        quality_status = rng.choice(quality_statuses, p=[0.79, 0.15, 0.06])
        inventory_status = rng.choice(inventory_statuses, p=[0.60, 0.20, 0.20])
        base_output = max(40, int(rng.normal(280, 55)))
        plant_factor = {"华东工厂": 1.08, "华南工厂": 1.0, "西部工厂": 0.92}[plant]
        status_factor = 0.82 if order_status == "延迟" else 0.94 if order_status == "生产中" else 1.0
        output_units = max(20, int(base_output * plant_factor * status_factor))
        defect_rate = float(np.clip(rng.normal(0.022 if quality_status == "正常" else 0.055 if quality_status == "轻微缺陷" else 0.11, 0.012), 0.002, 0.30))
        defective_units = max(0, int(round(output_units * defect_rate)))
        scrap_cost_usd = defective_units * rng.uniform(1.8, 8.2)
        on_time_flag = 0 if order_status == "延迟" else 1
        delay_minutes = int(max(0, rng.normal(12, 14))) if order_status != "延迟" else int(max(30, rng.normal(165, 35)))
        cycle_minutes = round(max(12, rng.normal(54, 10)), 2)
        rows_out.append(
            {
                "production_id": f"M{idx + 1:07d}",
                "production_date": date,
                "plant": plant,
                "line_name": line_name,
                "product_family": product_family,
                "product_name": product_name,
                "sku": sku,
                "supplier": supplier,
                "warehouse_region": warehouse_region,
                "shift_name": shift_name,
                "order_status": order_status,
                "quality_status": quality_status,
                "inventory_status": inventory_status,
                "output_units": output_units,
                "defective_units": defective_units,
                "defect_rate": round(defect_rate, 4),
                "scrap_cost_usd": round(scrap_cost_usd, 2),
                "on_time_flag": on_time_flag,
                "delay_minutes": delay_minutes,
                "cycle_minutes": cycle_minutes,
            }
        )

    production_orders = pd.DataFrame(rows_out)
    defects = production_orders.loc[
        production_orders["defective_units"] > 0,
        ["production_id", "production_date", "plant", "line_name", "product_family", "quality_status", "defective_units", "scrap_cost_usd"],
    ].copy()
    inventory = (
        production_orders.groupby(["warehouse_region", "product_family", "product_name", "inventory_status"], as_index=False)
        .agg(output_units=("output_units", "sum"), defective_units=("defective_units", "sum"))
    )
    shipments = (
        production_orders.groupby(["production_date", "plant", "supplier"], as_index=False)
        .agg(output_units=("output_units", "sum"), delay_minutes=("delay_minutes", "mean"))
        .rename(columns={"production_date": "shipment_date"})
    )
    return {"production_orders": production_orders, "defects": defects, "inventory": inventory, "shipments": shipments}


def marketplace_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-04-01", periods=50, freq="D")
    cities = ["上海", "北京", "广州", "成都", "杭州"]
    seller_tiers = ["长尾商家", "成长商家", "头部商家"]
    merchant_types = ["餐饮", "零售", "服务", "生鲜"]
    categories = {"餐饮": ["正餐", "轻食"], "零售": ["数码", "家居"], "服务": ["美容", "洗护"], "生鲜": ["水果", "冷链"]}
    campaigns = ["新客券", "周末闪促", "城市活动", "会员返券"]
    buyer_segments = ["新客", "复购客", "高频用户"]
    service_modes = ["到店", "即时配送", "次日达"]
    fulfillment_statuses = ["已完成", "配送中", "已取消"]
    complaint_statuses = ["无投诉", "处理中", "已结案"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        city = rng.choice(cities, p=[0.28, 0.22, 0.20, 0.16, 0.14])
        merchant_type = rng.choice(merchant_types, p=[0.35, 0.24, 0.21, 0.20])
        category = merchant_type
        subcategory = rng.choice(categories[merchant_type])
        seller_tier = rng.choice(seller_tiers, p=[0.56, 0.30, 0.14])
        seller_name = f"{city}-{subcategory}-{rng.integers(1, 40):02d}"
        sku = f"{subcategory[:2]}-{rng.integers(100, 999)}"
        campaign_name = rng.choice(campaigns)
        buyer_segment = rng.choice(buyer_segments, p=[0.34, 0.46, 0.20])
        service_mode = rng.choice(service_modes, p=[0.22, 0.56, 0.22])
        fulfillment_status = rng.choice(fulfillment_statuses, p=[0.80, 0.10, 0.10])
        complaint_status = rng.choice(complaint_statuses, p=[0.86, 0.08, 0.06])
        orders = max(1, int(rng.poisson(3.2) + 1))
        basket = rng.uniform(12, 58) * (1.2 if service_mode == "即时配送" else 1.0)
        gmv_usd = orders * basket
        subsidy_usd = gmv_usd * rng.uniform(0.02, 0.11)
        commission_usd = gmv_usd * rng.uniform(0.08, 0.16)
        complaint_cost_usd = 0.0 if complaint_status == "无投诉" else gmv_usd * rng.uniform(0.01, 0.08)
        rows_out.append(
            {
                "transaction_id": f"O{idx + 1:07d}",
                "transaction_date": date,
                "city": city,
                "seller_tier": seller_tier,
                "seller_name": seller_name,
                "merchant_type": merchant_type,
                "category": category,
                "subcategory": subcategory,
                "sku": sku,
                "campaign_name": campaign_name,
                "buyer_segment": buyer_segment,
                "service_mode": service_mode,
                "fulfillment_status": fulfillment_status,
                "complaint_status": complaint_status,
                "orders": orders,
                "gmv_usd": round(gmv_usd, 2),
                "subsidy_usd": round(subsidy_usd, 2),
                "commission_usd": round(commission_usd, 2),
                "complaint_cost_usd": round(complaint_cost_usd, 2),
            }
        )

    transactions = pd.DataFrame(rows_out)
    sellers = transactions[["seller_name", "seller_tier", "merchant_type", "city"]].drop_duplicates().reset_index(drop=True)
    buyers = transactions.groupby(["transaction_date", "buyer_segment"], as_index=False).agg(
        orders=("orders", "sum"),
        gmv_usd=("gmv_usd", "sum"),
    )
    complaints = transactions.loc[transactions["complaint_status"] != "无投诉", ["transaction_id", "transaction_date", "city", "seller_name", "complaint_status", "complaint_cost_usd"]].copy()
    return {"transactions": transactions, "sellers": sellers, "buyers": buyers, "complaints": complaints}


def finance_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-05-01", periods=65, freq="D")
    channels = ["线上直贷", "合作渠道", "地推", "银行转介"]
    segments = ["优质客群", "成长客群", "风险客群"]
    products = ["消费贷", "小微贷", "教育贷", "车主贷"]
    regions = ["华东", "华南", "华北", "中西部"]
    risk_grades = ["A", "B", "C", "D"]
    repayment_statuses = ["正常", "部分还款", "提前结清"]
    overdue_statuses = ["未逾期", "1-30天", "31-90天", "90天以上"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        channel = rng.choice(channels, p=[0.36, 0.26, 0.18, 0.20])
        customer_segment = rng.choice(segments, p=[0.44, 0.36, 0.20])
        product_name = rng.choice(products, p=[0.34, 0.26, 0.18, 0.22])
        region = rng.choice(regions, p=[0.31, 0.24, 0.21, 0.24])
        branch_name = f"{region}-支行{rng.integers(1, 10)}"
        risk_grade = rng.choice(risk_grades, p=[0.26, 0.38, 0.24, 0.12])
        term_bucket = rng.choice(["30天", "90天", "180天", "360天"], p=[0.18, 0.34, 0.28, 0.20])
        repayment_status = rng.choice(repayment_statuses, p=[0.72, 0.18, 0.10])
        overdue_status = rng.choice(overdue_statuses, p=[0.81, 0.11, 0.06, 0.02])
        disbursed_usd = rng.uniform(600, 18_000) * (1.35 if customer_segment == "优质客群" else 0.88 if customer_segment == "风险客群" else 1.0)
        interest_income_usd = disbursed_usd * rng.uniform(0.04, 0.16)
        overdue_amount_usd = 0.0 if overdue_status == "未逾期" else disbursed_usd * rng.uniform(0.03, 0.28)
        provision_usd = overdue_amount_usd * rng.uniform(0.20, 0.65)
        net_margin_usd = interest_income_usd - provision_usd - disbursed_usd * rng.uniform(0.002, 0.01)
        rows_out.append(
            {
                "loan_id": f"F{idx + 1:07d}",
                "disbursement_date": date,
                "channel": channel,
                "customer_segment": customer_segment,
                "product_name": product_name,
                "region": region,
                "branch_name": branch_name,
                "risk_grade": risk_grade,
                "term_bucket": term_bucket,
                "repayment_status": repayment_status,
                "overdue_status": overdue_status,
                "disbursed_usd": round(disbursed_usd, 2),
                "interest_income_usd": round(interest_income_usd, 2),
                "overdue_amount_usd": round(overdue_amount_usd, 2),
                "provision_usd": round(provision_usd, 2),
                "net_margin_usd": round(net_margin_usd, 2),
            }
        )

    loans = pd.DataFrame(rows_out)
    repayments = loans.groupby(["disbursement_date", "repayment_status"], as_index=False).agg(
        disbursed_usd=("disbursed_usd", "sum"),
        overdue_amount_usd=("overdue_amount_usd", "sum"),
    ).rename(columns={"disbursement_date": "repayment_date"})
    risk_events = loans.loc[loans["overdue_status"] != "未逾期", ["loan_id", "disbursement_date", "risk_grade", "overdue_status", "overdue_amount_usd"]].copy()
    customers = loans[["customer_segment", "channel", "region", "risk_grade"]].drop_duplicates().reset_index(drop=True)
    return {"loans": loans, "repayments": repayments, "risk_events": risk_events, "customers": customers}


def logistics_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-06-01", periods=55, freq="D")
    regions = ["华东", "华南", "华北", "西南"]
    courier_types = ["自营", "加盟", "众包"]
    carriers = ["顺达物流", "云速配送", "星辰快运"]
    service_levels = ["当日达", "次日达", "标准达"]
    route_types = ["同城", "省内", "跨省"]
    delivery_statuses = ["已签收", "运输中", "延误", "取消"]
    claim_statuses = ["无理赔", "处理中", "已赔付"]
    segments = ["电商商家", "企业客户", "个人用户"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        region = rng.choice(regions, p=[0.34, 0.26, 0.22, 0.18])
        station_name = f"{region}-站点{rng.integers(1, 12)}"
        courier_type = rng.choice(courier_types, p=[0.42, 0.34, 0.24])
        carrier_name = rng.choice(carriers)
        service_level = rng.choice(service_levels, p=[0.16, 0.36, 0.48])
        route_type = rng.choice(route_types, p=[0.38, 0.34, 0.28])
        customer_segment = rng.choice(segments, p=[0.46, 0.28, 0.26])
        delivery_status = rng.choice(delivery_statuses, p=[0.74, 0.14, 0.08, 0.04])
        claim_status = rng.choice(claim_statuses, p=[0.89, 0.07, 0.04])
        parcel_count = max(1, int(rng.poisson(5.5)))
        delivery_revenue_usd = parcel_count * rng.uniform(2.4, 11.5)
        on_time_flag = 0 if delivery_status == "延误" else 1
        late_minutes = int(max(0, rng.normal(8, 9))) if delivery_status != "延误" else int(max(25, rng.normal(105, 28)))
        claim_amount_usd = 0.0 if claim_status == "无理赔" else parcel_count * rng.uniform(1.5, 12.0)
        rows_out.append(
            {
                "shipment_id": f"L{idx + 1:07d}",
                "shipment_date": date,
                "region": region,
                "station_name": station_name,
                "courier_type": courier_type,
                "carrier_name": carrier_name,
                "service_level": service_level,
                "route_type": route_type,
                "customer_segment": customer_segment,
                "delivery_status": delivery_status,
                "claim_status": claim_status,
                "parcel_count": parcel_count,
                "delivery_revenue_usd": round(delivery_revenue_usd, 2),
                "on_time_flag": on_time_flag,
                "late_minutes": late_minutes,
                "claim_amount_usd": round(claim_amount_usd, 2),
            }
        )

    shipments = pd.DataFrame(rows_out)
    delivery_events = shipments.groupby(["shipment_date", "region", "delivery_status"], as_index=False).agg(
        parcel_count=("parcel_count", "sum"),
        late_minutes=("late_minutes", "mean"),
    )
    couriers = shipments[["station_name", "courier_type", "carrier_name", "service_level"]].drop_duplicates().reset_index(drop=True)
    claims = shipments.loc[shipments["claim_status"] != "无理赔", ["shipment_id", "shipment_date", "region", "claim_status", "claim_amount_usd"]].copy()
    return {"shipments": shipments, "delivery_events": delivery_events, "couriers": couriers, "claims": claims}


def media_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-07-01", periods=48, freq="D")
    content_types = ["短视频", "直播回放", "图文", "社区帖"]
    topics = ["科技", "财经", "生活", "游戏", "教育"]
    creator_tiers = ["腰部创作者", "头部创作者", "新锐创作者"]
    channels = ["推荐流", "搜索", "订阅", "外部分享"]
    segments = ["游客", "注册用户", "订阅用户"]
    regions = ["中国", "东南亚", "欧美"]
    subscription_statuses = ["未订阅", "试用中", "已订阅"]
    moderation_statuses = ["正常", "限流", "下架"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        content_type = rng.choice(content_types, p=[0.42, 0.14, 0.24, 0.20])
        topic = rng.choice(topics)
        creator_tier = rng.choice(creator_tiers, p=[0.48, 0.18, 0.34])
        creator_name = f"{topic}-creator-{rng.integers(1, 60):02d}"
        distribution_channel = rng.choice(channels, p=[0.54, 0.14, 0.20, 0.12])
        user_segment = rng.choice(segments, p=[0.34, 0.42, 0.24])
        region = rng.choice(regions, p=[0.58, 0.20, 0.22])
        subscription_status = rng.choice(subscription_statuses, p=[0.54, 0.16, 0.30])
        moderation_status = rng.choice(moderation_statuses, p=[0.88, 0.09, 0.03])
        views = max(100, int(rng.normal(4800, 1300)))
        watch_minutes = views * rng.uniform(0.6, 2.8)
        likes = int(views * rng.uniform(0.03, 0.12))
        shares = int(views * rng.uniform(0.005, 0.025))
        subscriptions = int(views * rng.uniform(0.001, 0.012))
        ad_revenue_usd = views / 1000 * rng.uniform(1.8, 9.5)
        rows_out.append(
            {
                "content_event_id": f"C{idx + 1:07d}",
                "event_date": date,
                "content_type": content_type,
                "topic": topic,
                "creator_tier": creator_tier,
                "creator_name": creator_name,
                "distribution_channel": distribution_channel,
                "user_segment": user_segment,
                "region": region,
                "subscription_status": subscription_status,
                "moderation_status": moderation_status,
                "views": views,
                "watch_minutes": round(watch_minutes, 1),
                "likes": likes,
                "shares": shares,
                "subscriptions": subscriptions,
                "ad_revenue_usd": round(ad_revenue_usd, 2),
            }
        )

    content_events = pd.DataFrame(rows_out)
    users = content_events.groupby(["event_date", "user_segment", "subscription_status"], as_index=False).agg(
        views=("views", "sum"),
        subscriptions=("subscriptions", "sum"),
    ).rename(columns={"event_date": "activity_date"})
    creators = content_events[["creator_name", "creator_tier", "topic", "content_type"]].drop_duplicates().reset_index(drop=True)
    subscriptions_df = content_events.loc[:, ["content_event_id", "event_date", "user_segment", "subscription_status", "subscriptions"]].copy()
    return {"content_events": content_events, "users": users, "creators": creators, "subscriptions": subscriptions_df}


def healthcare_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-08-01", periods=52, freq="D")
    regions = ["华东", "华南", "华北", "西南"]
    departments = ["内科", "外科", "口腔", "体检", "康复"]
    doctor_levels = ["主任", "副主任", "主治", "住院"]
    payer_types = ["自费", "商保", "团检", "医保"]
    service_lines = ["门诊", "日间手术", "体检", "康复"]
    patient_segments = ["新患者", "复诊患者", "高价值患者"]
    visit_statuses = ["已就诊", "爽约", "改约"]
    followup_statuses = ["无需随访", "待随访", "已随访"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        hospital_region = rng.choice(regions, p=[0.32, 0.26, 0.22, 0.20])
        clinic_name = f"{hospital_region}-院区{rng.integers(1, 8)}"
        department = rng.choice(departments)
        doctor_level = rng.choice(doctor_levels, p=[0.12, 0.20, 0.36, 0.32])
        payer_type = rng.choice(payer_types, p=[0.28, 0.18, 0.12, 0.42])
        service_line = rng.choice(service_lines, p=[0.48, 0.10, 0.24, 0.18])
        patient_segment = rng.choice(patient_segments, p=[0.38, 0.44, 0.18])
        visit_status = rng.choice(visit_statuses, p=[0.80, 0.08, 0.12])
        followup_status = rng.choice(followup_statuses, p=[0.46, 0.22, 0.32])
        visits = 0 if visit_status == "爽约" else 1
        billed_revenue_usd = visits * rng.uniform(28, 360) * (1.35 if doctor_level == "主任" else 1.0)
        treatment_cost_usd = billed_revenue_usd * rng.uniform(0.34, 0.68)
        margin_usd = billed_revenue_usd - treatment_cost_usd
        wait_minutes = int(max(0, rng.normal(26, 12)))
        no_show_count = 1 if visit_status == "爽约" else 0
        rows_out.append(
            {
                "visit_id": f"H{idx + 1:07d}",
                "visit_date": date,
                "hospital_region": hospital_region,
                "clinic_name": clinic_name,
                "department": department,
                "doctor_level": doctor_level,
                "payer_type": payer_type,
                "service_line": service_line,
                "patient_segment": patient_segment,
                "visit_status": visit_status,
                "followup_status": followup_status,
                "visits": visits,
                "billed_revenue_usd": round(billed_revenue_usd, 2),
                "treatment_cost_usd": round(treatment_cost_usd, 2),
                "margin_usd": round(margin_usd, 2),
                "wait_minutes": wait_minutes,
                "no_show_count": no_show_count,
            }
        )

    appointments = pd.DataFrame(rows_out)
    claims = appointments.groupby(["visit_date", "payer_type", "visit_status"], as_index=False).agg(
        billed_revenue_usd=("billed_revenue_usd", "sum"),
        no_show_count=("no_show_count", "sum"),
    )
    followups = appointments.loc[:, ["visit_id", "visit_date", "patient_segment", "followup_status", "margin_usd"]].copy()
    clinics = appointments[["hospital_region", "clinic_name", "department", "doctor_level"]].drop_duplicates().reset_index(drop=True)
    return {"appointments": appointments, "claims": claims, "followups": followups, "clinics": clinics}


def education_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-09-01", periods=54, freq="D")
    program_types = ["职业教育", "语言培训", "K12", "企业内训"]
    subject_areas = ["编程", "英语", "管理", "设计", "数据分析"]
    campus_regions = ["华东", "华南", "华北", "西南"]
    cohorts = ["春季班", "暑期班", "秋季班", "周末班"]
    channels = ["自然咨询", "投流", "校招合作", "企业销售"]
    learner_segments = ["新学员", "续费学员", "企业学员"]
    instructor_tiers = ["金牌讲师", "高级讲师", "助教"]
    enrollment_statuses = ["已报名", "待付款", "已退款"]
    completion_statuses = ["学习中", "已结课", "中途流失"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        program_type = rng.choice(program_types)
        subject_area = rng.choice(subject_areas)
        campus_region = rng.choice(campus_regions, p=[0.32, 0.24, 0.22, 0.22])
        cohort_name = rng.choice(cohorts)
        acquisition_channel = rng.choice(channels, p=[0.30, 0.28, 0.16, 0.26])
        learner_segment = rng.choice(learner_segments, p=[0.42, 0.33, 0.25])
        instructor_tier = rng.choice(instructor_tiers, p=[0.18, 0.44, 0.38])
        enrollment_status = rng.choice(enrollment_statuses, p=[0.76, 0.12, 0.12])
        completion_status = rng.choice(completion_statuses, p=[0.48, 0.34, 0.18])
        tuition_revenue_usd = 0.0 if enrollment_status != "已报名" else rng.uniform(120, 2200)
        refund_amount_usd = 0.0 if enrollment_status != "已退款" else tuition_revenue_usd * rng.uniform(0.3, 1.0)
        study_minutes = max(0, int(rng.normal(320, 110))) if enrollment_status == "已报名" else 0
        lessons_completed = max(0, int(rng.normal(8, 4))) if completion_status != "中途流失" else max(0, int(rng.normal(3, 2)))
        completion_count = 1 if completion_status == "已结课" else 0
        rows_out.append(
            {
                "learning_id": f"E{idx + 1:07d}",
                "learning_date": date,
                "program_type": program_type,
                "subject_area": subject_area,
                "campus_region": campus_region,
                "cohort_name": cohort_name,
                "acquisition_channel": acquisition_channel,
                "learner_segment": learner_segment,
                "instructor_tier": instructor_tier,
                "enrollment_status": enrollment_status,
                "completion_status": completion_status,
                "tuition_revenue_usd": round(tuition_revenue_usd, 2),
                "refund_amount_usd": round(refund_amount_usd, 2),
                "study_minutes": study_minutes,
                "lessons_completed": lessons_completed,
                "completion_count": completion_count,
            }
        )

    learning_events = pd.DataFrame(rows_out)
    courses = learning_events.groupby(["learning_date", "program_type", "completion_status"], as_index=False).agg(
        tuition_revenue_usd=("tuition_revenue_usd", "sum"),
        lessons_completed=("lessons_completed", "sum"),
    )
    learners = learning_events[["learner_segment", "campus_region", "acquisition_channel", "program_type"]].drop_duplicates().reset_index(drop=True)
    completions = learning_events.loc[:, ["learning_id", "learning_date", "completion_status", "completion_count", "study_minutes"]].copy()
    return {"learning_events": learning_events, "courses": courses, "learners": learners, "completions": completions}


def crypto_dataset(rng: np.random.Generator, rows: int) -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-10-01", periods=58, freq="D")
    chains = ["Ethereum", "Solana", "BNB Chain", "Base"]
    venue_types = ["现货", "合约", "DEX", "跨链桥"]
    token_sectors = ["Layer1", "Meme", "DeFi", "AI", "Stablecoin"]
    assets = {
        "Layer1": ["ETH", "SOL", "BNB"],
        "Meme": ["DOGE", "PEPE"],
        "DeFi": ["UNI", "AAVE", "MKR"],
        "AI": ["FET", "TAO"],
        "Stablecoin": ["USDT", "USDC"],
    }
    wallet_segments = ["散户", "高频交易者", "机构", "巨鲸"]
    regions = ["APAC", "EMEA", "AMER"]
    tx_statuses = ["success", "pending", "failed"]
    risk_statuses = ["normal", "monitor", "alert"]
    rows_out: list[dict[str, object]] = []

    for idx in range(rows):
        date = dates[int(rng.integers(0, len(dates)))]
        chain_name = rng.choice(chains, p=[0.36, 0.24, 0.22, 0.18])
        venue_type = rng.choice(venue_types, p=[0.34, 0.24, 0.28, 0.14])
        token_sector = rng.choice(token_sectors, p=[0.22, 0.14, 0.26, 0.16, 0.22])
        asset_symbol = rng.choice(assets[token_sector])
        wallet_segment = rng.choice(wallet_segments, p=[0.46, 0.24, 0.18, 0.12])
        trader_tier = rng.choice(["新账户", "活跃账户", "VIP"], p=[0.32, 0.50, 0.18])
        region = rng.choice(regions, p=[0.44, 0.28, 0.28])
        tx_status = rng.choice(tx_statuses, p=[0.88, 0.06, 0.06])
        risk_status = rng.choice(risk_statuses, p=[0.84, 0.11, 0.05])
        traded_volume_usd = rng.uniform(5_000, 280_000) * (1.65 if wallet_segment == "巨鲸" else 1.0)
        fee_revenue_usd = traded_volume_usd * rng.uniform(0.0008, 0.006)
        active_addresses = max(1, int(rng.normal(140, 40)))
        gas_cost_usd = traded_volume_usd * rng.uniform(0.0003, 0.0024)
        rows_out.append(
            {
                "activity_id": f"K{idx + 1:07d}",
                "block_date": date,
                "chain_name": chain_name,
                "venue_type": venue_type,
                "token_sector": token_sector,
                "asset_symbol": asset_symbol,
                "wallet_segment": wallet_segment,
                "trader_tier": trader_tier,
                "region": region,
                "tx_status": tx_status,
                "risk_status": risk_status,
                "traded_volume_usd": round(traded_volume_usd, 2),
                "fee_revenue_usd": round(fee_revenue_usd, 2),
                "active_addresses": active_addresses,
                "gas_cost_usd": round(gas_cost_usd, 2),
            }
        )

    market_activity = pd.DataFrame(rows_out)
    liquidity = market_activity.groupby(["block_date", "chain_name", "venue_type"], as_index=False).agg(
        traded_volume_usd=("traded_volume_usd", "sum"),
        fee_revenue_usd=("fee_revenue_usd", "sum"),
    )
    wallets = market_activity[["wallet_segment", "trader_tier", "region", "chain_name"]].drop_duplicates().reset_index(drop=True)
    alerts = market_activity.loc[market_activity["risk_status"] != "normal", ["activity_id", "block_date", "asset_symbol", "risk_status", "traded_volume_usd"]].copy()
    return {"market_activity": market_activity, "liquidity": liquidity, "wallets": wallets, "alerts": alerts}


GENERATORS = {
    "retail": retail_dataset,
    "saas": saas_dataset,
    "manufacturing": manufacturing_dataset,
    "marketplace": marketplace_dataset,
    "finance": finance_dataset,
    "logistics": logistics_dataset,
    "media": media_dataset,
    "healthcare": healthcare_dataset,
    "education": education_dataset,
    "crypto": crypto_dataset,
}


def build_dimension_plan(spec: IndustrySpec, fact: pd.DataFrame) -> dict[str, object]:
    ignore = {spec.time_col}
    measures = detect_measures(fact, ignore)
    return {
        "fact_table": spec.fact_table,
        "grain": spec.grain,
        "measures": measures,
        "dimension_packs": spec.dimension_packs,
        "hierarchies": spec.hierarchies,
        "priority_cuts": spec.priority_cuts,
    }


def analyze_industry(spec: IndustrySpec, tables: dict[str, pd.DataFrame], out_dir: Path) -> dict[str, object]:
    fact = add_time_columns(tables[spec.fact_table], spec.time_col)
    tables = dict(tables)
    tables[spec.fact_table] = fact
    out_dir.mkdir(parents=True, exist_ok=True)
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(tables_dir / f"{name}.csv", index=False)

    plan = build_dimension_plan(spec, fact)
    write_text(out_dir / "dimension_plan.json", json.dumps(plan, ensure_ascii=False, indent=2))

    time_metric = fact.groupby("day", as_index=False).agg(
        primary_metric=(spec.primary_metric, "sum"),
        records=(spec.primary_metric, "size"),
    )
    if "request_count" in fact.columns:
        time_metric["secondary_metric"] = fact.groupby("day")["request_count"].sum().values
    elif "profit" in fact.columns:
        time_metric["secondary_metric"] = fact.groupby("day")["profit"].sum().values
    elif "defective_units" in fact.columns:
        time_metric["secondary_metric"] = fact.groupby("day")["defective_units"].sum().values
    else:
        time_metric["secondary_metric"] = np.nan
    time_metric["mom_delta"] = time_metric["primary_metric"].diff().fillna(0)
    time_metric.to_csv(out_dir / "daily_trend.csv", index=False)

    slice_outputs: list[tuple[str, pd.DataFrame]] = []
    for dim in spec.dimensions[:3]:
        agg_map: dict[str, tuple[str, str]] = {
            spec.primary_metric: (spec.primary_metric, "sum"),
            "records": (spec.primary_metric, "size"),
        }
        if "profit" in fact.columns and dim != "profit":
            agg_map["profit"] = ("profit", "sum")
        if "cost_usd" in fact.columns and dim != "cost_usd":
            agg_map["cost_usd"] = ("cost_usd", "sum")
        if "margin_usd" in fact.columns and dim != "margin_usd":
            agg_map["margin_usd"] = ("margin_usd", "sum")
        if "defective_units" in fact.columns and dim != "defective_units":
            agg_map["defective_units"] = ("defective_units", "sum")
        cut = fact.groupby(dim, as_index=False).agg(**agg_map).sort_values(spec.primary_metric, ascending=False).head(12)
        if "refund_amount" in fact.columns:
            refund_by_dim = fact.groupby(dim, as_index=False)["refund_amount"].sum()
            cut = cut.merge(refund_by_dim, on=dim, how="left")
        if {"defective_units", "output_units"}.issubset(fact.columns):
            defect_rate = fact.groupby(dim).agg(output_units=("output_units", "sum"), defective_units=("defective_units", "sum")).reset_index()
            defect_rate["defect_rate"] = defect_rate["defective_units"] / defect_rate["output_units"].replace(0, np.nan)
            cut = cut.merge(defect_rate[[dim, "defect_rate"]], on=dim, how="left")
        slice_outputs.append((dim, cut))
        cut.to_csv(out_dir / f"slice_{dim}.csv", index=False)

    status_frames: list[pd.DataFrame] = []
    for dim in spec.status_dimensions:
        if dim not in fact.columns:
            continue
        cut = fact.groupby(dim, as_index=False).agg(
            primary_metric=(spec.primary_metric, "sum"),
            records=(spec.primary_metric, "size"),
        )
        status_frames.append(cut.assign(status_dimension=dim))
    status_combined = pd.concat(status_frames, ignore_index=True) if status_frames else pd.DataFrame()
    if not status_combined.empty:
        status_combined.to_csv(out_dir / "status_breakdown.csv", index=False)

    hierarchy_dim = spec.hierarchies[1].split(" > ")
    hierarchy_cut = (
        fact.groupby(hierarchy_dim, as_index=False)
        .agg(primary_metric=(spec.primary_metric, "sum"))
        .sort_values("primary_metric", ascending=False)
        .head(15)
    )
    hierarchy_cut.to_csv(out_dir / "hierarchy_drill.csv", index=False)

    fact_total = float(fact[spec.primary_metric].sum())
    validation = pd.DataFrame(
        [
            {
                "check_name": "fact_total_vs_daily_total",
                "left_value": fact_total,
                "right_value": float(time_metric["primary_metric"].sum()),
                "difference": float(fact_total - time_metric["primary_metric"].sum()),
            },
            {
                "check_name": "fact_total_vs_first_slice_total",
                "left_value": fact_total,
                "right_value": float(slice_outputs[0][1][spec.primary_metric].sum()),
                "difference": float(fact_total - slice_outputs[0][1][spec.primary_metric].sum()),
            },
        ]
    )
    validation.to_csv(out_dir / "validation_crosscheck.csv", index=False)

    peak_day = time_metric.sort_values("primary_metric", ascending=False).iloc[0]
    trough_day = time_metric.sort_values("primary_metric", ascending=True).iloc[0]
    anomaly_threshold = float(time_metric["primary_metric"].mean() + 1.5 * time_metric["primary_metric"].std(ddof=0))
    anomaly_days = time_metric.loc[time_metric["primary_metric"] >= anomaly_threshold, "day"].tolist()

    report_lines: list[str] = []
    report_lines.append(f"# {spec.label} Mock BI Regression")
    report_lines.append("")
    report_lines.append("## 数据概览")
    report_lines.append(f"- 主事实表: `{spec.fact_table}`")
    report_lines.append(f"- 行粒度: `{spec.grain}`")
    report_lines.append(f"- 主事实表行数: {fmt_int(len(fact))}")
    report_lines.append(f"- 时间字段: `{spec.time_col}`")
    report_lines.append(f"- 命中的维度包: {', '.join(spec.dimension_packs)}")
    report_lines.append(f"- 识别到的 measure: {', '.join(plan['measures'])}")
    report_lines.append("")
    report_lines.append("## Tableau 风格维度规划")
    report_lines.append(f"- Hierarchy: {', '.join(spec.hierarchies)}")
    report_lines.append(f"- Priority cuts: {', '.join(spec.priority_cuts)}")
    report_lines.append("")
    report_lines.append("## 核心结论")
    report_lines.append(f"- 主指标 `{spec.primary_metric}` 总量: {fmt_money(fact_total) if 'usd' in spec.primary_metric or 'sales' in spec.primary_metric or 'profit' in spec.primary_metric else fmt_int(fact_total)}")
    report_lines.append(f"- 峰值日期: `{peak_day['day']}`，主指标为 `{fmt_money(peak_day['primary_metric']) if isinstance(peak_day['primary_metric'], float) else peak_day['primary_metric']}`")
    report_lines.append(f"- 低谷日期: `{trough_day['day']}`，主指标为 `{fmt_money(trough_day['primary_metric']) if isinstance(trough_day['primary_metric'], float) else trough_day['primary_metric']}`")
    report_lines.append(f"- 异常日期数: `{len(anomaly_days)}`，异常日: `{', '.join(anomaly_days[:8]) if anomaly_days else '无明显异常峰值'}`")
    report_lines.append("")
    report_lines.append("## 维度切片摘要")
    for dim, frame in slice_outputs:
        top_row = frame.iloc[0]
        top_value = top_row[spec.primary_metric]
        display_value = fmt_money(top_value) if isinstance(top_value, float) else fmt_int(top_value)
        report_lines.append(f"- `{dim}` Top 1: `{top_row[dim]}`，对应 `{spec.primary_metric}={display_value}`")
    if not status_combined.empty:
        report_lines.append(f"- 状态维度已覆盖: {', '.join(spec.status_dimensions)}")
    report_lines.append("")
    report_lines.append("## 测试结论")
    report_lines.append("- 已覆盖 1 个时间维度、至少 3 个业务维度、至少 1 个状态 / 生命周期维度。")
    report_lines.append("- 已输出趋势、层级钻取、状态切片和交叉校验结果。")
    report_lines.append("- 执行环境：python3、pandas、numpy；回归基于本地 synthetic dataset 完成。")
    report_lines.append("")
    report_lines.append("## Caveat")
    report_lines.append("- 数据为 synthetic mock，仅用于验证 skill 的维度识别和分析流程，不代表真实业务口径。")
    report_lines.append("- 某些行业特定维度如真实营销归因、复杂库存周转、财务核销口径仍需在真实数据接入时单独补齐。")
    write_text(out_dir / "mock_bi_test_report.md", "\n".join(report_lines))

    return {
        "industry": spec.key,
        "label": spec.label,
        "rows": int(len(fact)),
        "size_profile": spec.preferred_size,
        "dimension_pack_count": len(spec.dimension_packs),
        "hierarchy_count": len(spec.hierarchies),
        "slice_count": len(slice_outputs),
        "status_dimension_count": len(spec.status_dimensions),
        "anomaly_days": len(anomaly_days),
        "report_path": str(out_dir / "mock_bi_test_report.md"),
    }


def resolve_requested_industries(industry_args: list[str]) -> list[IndustrySpec]:
    specs: list[IndustrySpec] = []
    for key in industry_args:
        if key not in SPECS:
            raise ValueError(f"unsupported industry: {key}")
        specs.append(SPECS[key])
    return specs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-industry synthetic BI regression tests.")
    parser.add_argument(
        "--industries",
        nargs="+",
        default=["retail", "saas", "manufacturing"],
        help="Industries to mock. Supported: retail saas manufacturing",
    )
    parser.add_argument(
        "--size-profile",
        choices=["small", "medium", "large", "mixed"],
        default="mixed",
        help="Use a single dataset size for all industries, or use the mixed profile from the industry matrix.",
    )
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for generated mock data and reports.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible synthetic datasets.")
    args = parser.parse_args()

    specs = resolve_requested_industries(args.industries)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, object]] = []

    for idx, spec in enumerate(specs):
        rng = np.random.default_rng(args.seed + idx * 97)
        size_name = spec.preferred_size if args.size_profile == "mixed" else args.size_profile
        rows = choose_size(size_name)
        tables = GENERATORS[spec.key](rng, rows)
        industry_out_dir = args.out_dir / spec.key
        summary = analyze_industry(spec, tables, industry_out_dir)
        summary["size_profile"] = size_name
        summary_rows.append(summary)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(args.out_dir / "industry_mock_summary.csv", index=False)

    lines: list[str] = []
    lines.append("# BI Skill Multi-Industry Mock Summary")
    lines.append("")
    lines.append("## 执行配置")
    lines.append(f"- Industries: {', '.join(args.industries)}")
    lines.append(f"- Size profile: {args.size_profile}")
    lines.append(f"- Random seed: {args.seed}")
    lines.append("- External BI platform dependency: None")
    lines.append("")
    lines.append("## 结果摘要")
    lines.append("| 行业 | 行数 | 维度包数 | Hierarchy 数 | 切片数 | 状态维度数 | 异常日数 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, row in summary_df.iterrows():
        lines.append(
            f"| {row['industry']} | {fmt_int(row['rows'])} | {fmt_int(row['dimension_pack_count'])} | "
            f"{fmt_int(row['hierarchy_count'])} | {fmt_int(row['slice_count'])} | {fmt_int(row['status_dimension_count'])} | "
            f"{fmt_int(row['anomaly_days'])} |"
        )
    lines.append("")
    lines.append("## 结论")
    lines.append(f"- 这组 mock regression 共覆盖 {len(args.industries)} 个行业：{', '.join(args.industries)}。")
    lines.append("- 每个行业都验证了 Tableau 风格的 `dimension / measure / hierarchy / set-like slice` 组织方式。")
    lines.append("- 输出目录中同时保留了原始 synthetic 表、趋势 CSV、维度切片 CSV、交叉校验和 Markdown 报告。")
    write_text(args.out_dir / "mock_regression_summary.md", "\n".join(lines))

    print(f"Generated multi-industry mock regression artifacts in: {args.out_dir}")


if __name__ == "__main__":
    main()
