"""Build normalized financial metrics from parsed statement facts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from .formatting import safe_div
from .statement_facts import QUARTERS, ReportFacts

GRAIN_CURRENT = "current"
GRAIN_YTD = "ytd"
GRAIN_ENDING = "ending"
UNIT_CNY = "CNY"
UNIT_RATIO = "ratio"


@dataclass(frozen=True)
class MetricPoint:
    key: str
    label: str
    quarter: str
    grain: str
    unit: str
    value: Optional[float]
    source_basis: str = "FIN_STMT"
    formula: str = ""
    source_refs: Tuple[str, ...] = ()


@dataclass
class MetricStore:
    points: Dict[Tuple[str, str], MetricPoint] = field(default_factory=dict)

    def add(self, point: MetricPoint) -> None:
        self.points[(point.key, point.quarter)] = point

    def get(self, key: str, quarter: str, *, required: bool = False) -> Optional[MetricPoint]:
        point = self.points.get((key, quarter))
        if required and point is None:
            raise KeyError(f"Missing metric: {key}.{quarter}")
        return point

    def value(self, key: str, quarter: str) -> Optional[float]:
        point = self.get(key, quarter)
        return point.value if point else None

    def series(self, key: str, quarters: Iterable[str] = QUARTERS) -> List[Optional[float]]:
        return [self.value(key, q) for q in quarters]

    def all(self) -> List[MetricPoint]:
        return list(self.points.values())


def build_metrics(facts: ReportFacts, *, source_basis: str = "FIN_STMT") -> MetricStore:
    store = MetricStore()

    for quarter in facts.quarters:
        pl_cur = facts.profit_current[quarter]
        pl_ytd = facts.profit_ytd[quarter]
        cf_cur = facts.cashflow_current[quarter]
        cf_ytd = facts.cashflow_ytd[quarter]
        bs_a = facts.balance_assets_ending[quarter]
        bs_l = facts.balance_liability_equity_ending[quarter]

        _add_statement_metric(store, facts, "revenue.current", "营业收入（单季）", quarter, GRAIN_CURRENT, pl_cur, "一、营业收入", "profit", "current", source_basis)
        _add_statement_metric(store, facts, "revenue.ytd", "营业收入（累计）", quarter, GRAIN_YTD, pl_ytd, "一、营业收入", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "cost.current", "营业成本（单季）", quarter, GRAIN_CURRENT, pl_cur, "减：营业成本", "profit", "current", source_basis)
        _add_statement_metric(store, facts, "cost.ytd", "营业成本（累计）", quarter, GRAIN_YTD, pl_ytd, "减：营业成本", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "sales_expense.ytd", "销售费用（累计）", quarter, GRAIN_YTD, pl_ytd, "销售费用", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "management_expense.ytd", "管理费用（累计）", quarter, GRAIN_YTD, pl_ytd, "管理费用", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "rd_expense.ytd", "研发费用（累计）", quarter, GRAIN_YTD, pl_ytd, "研发费用", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "finance_expense.ytd", "财务费用（累计）", quarter, GRAIN_YTD, pl_ytd, "财务费用", "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "operating_profit.current", "营业利润（单季）", quarter, GRAIN_CURRENT, pl_cur, '二、营业利润(亏损以"-"号填列)', "profit", "current", source_basis)
        _add_statement_metric(store, facts, "operating_profit.ytd", "营业利润（累计）", quarter, GRAIN_YTD, pl_ytd, '二、营业利润(亏损以"-"号填列)', "profit", "ytd", source_basis)
        _add_statement_metric(store, facts, "net_profit.current", "净利润（单季）", quarter, GRAIN_CURRENT, pl_cur, '四、净利润(净亏损以"-"号填列)', "profit", "current", source_basis)
        _add_statement_metric(store, facts, "net_profit.ytd", "净利润（累计）", quarter, GRAIN_YTD, pl_ytd, '四、净利润(净亏损以"-"号填列)', "profit", "ytd", source_basis)

        _add_statement_metric(store, facts, "ocf.current", "经营现金流（单季）", quarter, GRAIN_CURRENT, cf_cur, "经营活动产生的现金流量净额", "cashflow", "current", source_basis)
        _add_statement_metric(store, facts, "ocf.ytd", "经营现金流（累计）", quarter, GRAIN_YTD, cf_ytd, "经营活动产生的现金流量净额", "cashflow", "ytd", source_basis)
        _add_statement_metric(store, facts, "invest_cf.ytd", "投资现金流（累计）", quarter, GRAIN_YTD, cf_ytd, "投资活动产生的现金流量净额", "cashflow", "ytd", source_basis)
        _add_statement_metric(store, facts, "financing_cf.ytd", "筹资现金流（累计）", quarter, GRAIN_YTD, cf_ytd, "筹资活动产生的现金流量净额", "cashflow", "ytd", source_basis)
        _add_statement_metric(store, facts, "cash.cf.ending", "现金流量表期末现金", quarter, GRAIN_ENDING, cf_ytd, "四、期末现金及现金等价物余额", "cashflow", "ytd", source_basis)

        _add_statement_metric(store, facts, "cash.bs.ending", "期末货币资金", quarter, GRAIN_ENDING, bs_a, "货币资金", "balance_asset", "ending", source_basis)
        _add_statement_metric(store, facts, "accounts_receivable.ending", "期末应收账款", quarter, GRAIN_ENDING, bs_a, "应收账款", "balance_asset", "ending", source_basis)
        _add_statement_metric(store, facts, "total_assets.ending", "资产总计", quarter, GRAIN_ENDING, bs_a, "资产总计", "balance_asset", "ending", source_basis)
        _add_statement_metric(store, facts, "current_assets.ending", "流动资产合计", quarter, GRAIN_ENDING, bs_a, "流动资产合计", "balance_asset", "ending", source_basis)
        _add_statement_metric(store, facts, "accounts_payable.ending", "期末应付账款", quarter, GRAIN_ENDING, bs_l, "应付账款", "balance_liability_equity", "ending", source_basis)
        _add_statement_metric(store, facts, "current_liabilities.ending", "流动负债合计", quarter, GRAIN_ENDING, bs_l, "流动负债合计", "balance_liability_equity", "ending", source_basis)
        _add_statement_metric(store, facts, "total_liabilities.ending", "负债合计", quarter, GRAIN_ENDING, bs_l, "负债合计", "balance_liability_equity", "ending", source_basis)
        _add_statement_metric(store, facts, "equity.ending", "所有者权益合计", quarter, GRAIN_ENDING, bs_l, "所有者权益合计", "balance_liability_equity", "ending", source_basis)

        _derive_money_delta(store, "gross_profit.current", "毛利（单季）", quarter, "revenue.current", "cost.current", source_basis)
        _derive_money_delta(store, "gross_profit.ytd", "毛利（累计）", quarter, "revenue.ytd", "cost.ytd", source_basis)
        _derive_ratio(store, "gross_margin.current", "毛利率（单季）", quarter, "gross_profit.current", "revenue.current", GRAIN_CURRENT, source_basis)
        _derive_ratio(store, "gross_margin.ytd", "毛利率（累计）", quarter, "gross_profit.ytd", "revenue.ytd", GRAIN_YTD, source_basis)
        _derive_ratio(store, "net_margin.current", "净利率（单季）", quarter, "net_profit.current", "revenue.current", GRAIN_CURRENT, source_basis)
        _derive_ratio(store, "net_margin.ytd", "净利率（累计）", quarter, "net_profit.ytd", "revenue.ytd", GRAIN_YTD, source_basis)
        _derive_ratio(store, "ocf_net_profit_ratio.current", "OCF / 净利润（单季）", quarter, "ocf.current", "net_profit.current", GRAIN_CURRENT, source_basis)
        _derive_ratio(store, "ocf_net_profit_ratio.ytd", "OCF / 净利润（累计）", quarter, "ocf.ytd", "net_profit.ytd", GRAIN_YTD, source_basis)
        _derive_ratio(store, "debt_to_asset.ending", "资产负债率（期末）", quarter, "total_liabilities.ending", "total_assets.ending", GRAIN_ENDING, source_basis)

    for idx, quarter in enumerate(facts.quarters):
        if idx == 0:
            store.add(MetricPoint("revenue_qoq.current", "单季营收环比", quarter, GRAIN_CURRENT, UNIT_RATIO, None, source_basis, "Q1 has no prior-quarter comparison"))
            continue
        previous_quarter = facts.quarters[idx - 1]
        _derive_qoq(store, "revenue_qoq.current", "单季营收环比", quarter, "revenue.current", previous_quarter, source_basis)

    return store


def _add_statement_metric(
    store: MetricStore,
    facts: ReportFacts,
    key: str,
    label: str,
    quarter: str,
    grain: str,
    source: Dict[str, Optional[float]],
    item: str,
    statement: str,
    field: str,
    source_basis: str,
) -> None:
    value = source.get(item)
    source_key = facts.lineage_key(statement, quarter, item, field)
    store.add(MetricPoint(key, label, quarter, grain, UNIT_CNY, value, source_basis, source_refs=(source_key,)))


def _require(store: MetricStore, key: str, quarter: str) -> MetricPoint:
    return store.get(key, quarter, required=True)  # type: ignore[return-value]


def _derive_money_delta(store: MetricStore, key: str, label: str, quarter: str, left_key: str, right_key: str, source_basis: str) -> None:
    left = _require(store, left_key, quarter)
    right = _require(store, right_key, quarter)
    _assert_same_grain(left, right)
    _assert_same_unit(left, right)
    value = None if left.value is None or right.value is None else left.value - right.value
    store.add(
        MetricPoint(
            key,
            label,
            quarter,
            left.grain,
            UNIT_CNY,
            value,
            source_basis,
            f"{left_key} - {right_key}",
            left.source_refs + right.source_refs,
        )
    )


def _derive_ratio(store: MetricStore, key: str, label: str, quarter: str, numerator_key: str, denominator_key: str, grain: str, source_basis: str) -> None:
    numerator = _require(store, numerator_key, quarter)
    denominator = _require(store, denominator_key, quarter)
    _assert_same_grain(numerator, denominator)
    if numerator.grain != grain:
        raise ValueError(f"{key}.{quarter}: expected grain {grain}, got {numerator.grain}")
    if numerator.unit != denominator.unit:
        raise ValueError(f"{key}.{quarter}: cannot divide {numerator.unit} by {denominator.unit}")
    store.add(
        MetricPoint(
            key,
            label,
            quarter,
            grain,
            UNIT_RATIO,
            safe_div(numerator.value, denominator.value),
            source_basis,
            f"{numerator_key} / {denominator_key}",
            numerator.source_refs + denominator.source_refs,
        )
    )


def _derive_qoq(store: MetricStore, key: str, label: str, quarter: str, base_key: str, previous_quarter: str, source_basis: str) -> None:
    current = _require(store, base_key, quarter)
    previous = _require(store, base_key, previous_quarter)
    if current.grain != GRAIN_CURRENT or previous.grain != GRAIN_CURRENT:
        raise ValueError(f"{key}.{quarter}: 环比 must use current-period metrics")
    _assert_same_unit(current, previous)
    value = None if current.value is None or previous.value in (None, 0) else current.value / previous.value - 1
    store.add(
        MetricPoint(
            key,
            label,
            quarter,
            GRAIN_CURRENT,
            UNIT_RATIO,
            value,
            source_basis,
            f"{base_key}.{quarter} / {base_key}.{previous_quarter} - 1",
            current.source_refs + previous.source_refs,
        )
    )


def _assert_same_grain(left: MetricPoint, right: MetricPoint) -> None:
    if left.grain != right.grain:
        raise ValueError(f"Grain mismatch: {left.key}.{left.quarter}={left.grain}, {right.key}.{right.quarter}={right.grain}")


def _assert_same_unit(left: MetricPoint, right: MetricPoint) -> None:
    if left.unit != right.unit:
        raise ValueError(f"Unit mismatch: {left.key}.{left.quarter}={left.unit}, {right.key}.{right.quarter}={right.unit}")
