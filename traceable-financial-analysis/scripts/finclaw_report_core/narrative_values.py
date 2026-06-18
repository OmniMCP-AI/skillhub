"""Narrative-ready values derived only from normalized metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .formatting import fmt_ratio, fmt_yuan_as_wan
from .metrics import MetricStore


@dataclass(frozen=True)
class NarrativeValue:
    name: str
    metric_key: str
    quarter: str
    text: str


def build_narrative_values(metrics: MetricStore) -> Dict[str, NarrativeValue]:
    mapping = {
        "full_year_revenue": ("revenue.ytd", "Q4"),
        "full_year_net_profit": ("net_profit.ytd", "Q4"),
        "full_year_net_margin": ("net_margin.ytd", "Q4"),
        "full_year_ocf": ("ocf.ytd", "Q4"),
        "full_year_ocf_np_ratio": ("ocf_net_profit_ratio.ytd", "Q4"),
        "q4_revenue_current": ("revenue.current", "Q4"),
        "q4_revenue_qoq": ("revenue_qoq.current", "Q4"),
        "q4_ocf_np_ratio": ("ocf_net_profit_ratio.current", "Q4"),
        "q4_cash": ("cash.bs.ending", "Q4"),
        "q4_debt_to_asset": ("debt_to_asset.ending", "Q4"),
        "q4_accounts_receivable": ("accounts_receivable.ending", "Q4"),
        "rd_expense_ytd": ("rd_expense.ytd", "Q4"),
    }
    values: Dict[str, NarrativeValue] = {}
    for name, (metric_key, quarter) in mapping.items():
        point = metrics.get(metric_key, quarter)
        if point is None:
            continue
        text = fmt_ratio(point.value) if point.unit == "ratio" else fmt_yuan_as_wan(point.value)
        values[name] = NarrativeValue(name, metric_key, quarter, text)
    return values


def build_management_summary(metrics: MetricStore) -> List[str]:
    v = build_narrative_values(metrics)
    return [
        (
            f"全年营收 {v['full_year_revenue'].text} 万元、净利润 {v['full_year_net_profit'].text} 万元，"
            f"净利率 {v['full_year_net_margin'].text}，收入与利润同步上行。"
        ),
        (
            f"经营现金流累计 {v['full_year_ocf'].text} 万元，OCF/净利润（累计）"
            f"{v['full_year_ocf_np_ratio'].text}，现金质量总体较好。"
        ),
        (
            f"Q4 单季收入 {v['q4_revenue_current'].text} 万元，单季营收环比 "
            f"{v['q4_revenue_qoq'].text}；Q4 OCF/净利润（单季）{v['q4_ocf_np_ratio'].text}。"
        ),
        (
            f"期末货币资金 {v['q4_cash'].text} 万元，资产负债率 {v['q4_debt_to_asset'].text}；"
            f"期末应收账款 {v['q4_accounts_receivable'].text} 万元，需要继续跟踪账龄和回款。"
        ),
    ]
