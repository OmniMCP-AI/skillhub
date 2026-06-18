"""Build fixed dashboard rows from normalized metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .formatting import fmt_ratio, fmt_yuan_as_wan
from .metrics import MetricStore, UNIT_CNY, UNIT_RATIO
from .statement_facts import QUARTERS


@dataclass(frozen=True)
class DashboardRow:
    label: str
    metric_key: str
    grain: str
    unit: str
    values: Dict[str, str]
    full_year: str
    note: str


ROW_SPECS = (
    ("营业收入（万元，累计）", "revenue.ytd", "累计值；全年口径使用 Q4 本年累计"),
    ("营业收入（单季，万元）", "revenue.current", "单季金额；用于环比和季度趋势"),
    ("单季营收环比", "revenue_qoq.current", "仅使用单季收入计算，不使用累计收入"),
    ("毛利率（累计）", "gross_margin.ytd", "毛利 / 营收；累计口径"),
    ("净利率（累计）", "net_margin.ytd", "净利润 / 营收；累计口径"),
    ("营业利润（万元，累计）", "operating_profit.ytd", "利润表本年累计金额"),
    ("净利润（万元，累计）", "net_profit.ytd", "利润表本年累计金额"),
    ("经营现金流（累计，万元）", "ocf.ytd", "现金流量表本年累计金额"),
    ("OCF / 净利润（单季）", "ocf_net_profit_ratio.current", "经营现金流单季 / 净利润单季"),
    ("OCF / 净利润（累计）", "ocf_net_profit_ratio.ytd", "经营现金流累计 / 净利润累计"),
    ("期末货币资金（万元）", "cash.bs.ending", "资产负债表期末数；应与现金流期末现金勾稽"),
    ("资产总计（万元）", "total_assets.ending", "资产负债表期末数"),
    ("资产负债率（期末）", "debt_to_asset.ending", "负债合计 / 资产总计"),
    ("应收账款（万元，期末）", "accounts_receivable.ending", "资产负债表期末数"),
    ("研发费用（万元，累计）", "rd_expense.ytd", "利润表本年累计金额；研究费用映射为研发费用"),
)


def build_dashboard_rows(metrics: MetricStore) -> List[DashboardRow]:
    rows: List[DashboardRow] = []
    for label, key, note in ROW_SPECS:
        points = [metrics.get(key, q) for q in QUARTERS]
        existing = [p for p in points if p is not None]
        if not existing:
            continue
        first = existing[0]
        values = {quarter: _format_metric_value(metrics, key, quarter) for quarter in QUARTERS}
        full_year = _full_year_value(metrics, key)
        rows.append(DashboardRow(label, key, first.grain, first.unit, values, full_year, note))
    return rows


def _format_metric_value(metrics: MetricStore, key: str, quarter: str) -> str:
    point = metrics.get(key, quarter)
    if point is None:
        return "-"
    if point.unit == UNIT_CNY:
        return fmt_yuan_as_wan(point.value)
    if point.unit == UNIT_RATIO:
        return fmt_ratio(point.value)
    return "-" if point.value is None else str(point.value)


def _full_year_value(metrics: MetricStore, key: str) -> str:
    if key.endswith(".current") or key == "revenue_qoq.current":
        return "-"
    return _format_metric_value(metrics, key, "Q4")
