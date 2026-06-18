"""Metric, dashboard, and report consistency validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .dashboard_rows import DashboardRow
from .metrics import GRAIN_CURRENT, MetricStore, UNIT_CNY, UNIT_RATIO
from .statement_facts import QUARTERS, ReportFacts


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    issues: List[ValidationIssue]

    def raise_for_errors(self) -> None:
        errors = [issue for issue in self.issues if issue.severity == "ERROR"]
        if errors:
            rendered = "\n".join(f"{issue.code}: {issue.message}" for issue in errors)
            raise ValueError(rendered)


def validate_all(facts: ReportFacts, metrics: MetricStore, dashboard_rows: Iterable[DashboardRow]) -> ValidationResult:
    issues: List[ValidationIssue] = []
    issues.extend(validate_three_statement_checks(facts))
    issues.extend(validate_metric_definitions(metrics))
    issues.extend(validate_dashboard_rows(dashboard_rows, metrics))
    return ValidationResult(not any(issue.severity == "ERROR" for issue in issues), issues)


def validate_three_statement_checks(facts: ReportFacts) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for quarter in QUARTERS:
        assets = facts.balance_assets_ending.get(quarter, {})
        liabilities = facts.balance_liability_equity_ending.get(quarter, {})
        total_assets = assets.get("资产总计")
        total_liabilities = liabilities.get("负债合计")
        equity = liabilities.get("所有者权益合计")
        cash_bs = assets.get("货币资金")
        cash_cf = facts.cashflow_ytd.get(quarter, {}).get("四、期末现金及现金等价物余额")

        if None not in (total_assets, total_liabilities, equity):
            diff = abs((total_assets or 0) - (total_liabilities or 0) - (equity or 0))
            if diff > 0.01:
                issues.append(ValidationIssue("ERROR", "BS_NOT_BALANCED", f"{quarter}: 资产总计 != 负债合计 + 权益，差异 {diff}"))
        else:
            issues.append(ValidationIssue("ERROR", "BS_MISSING_TOTALS", f"{quarter}: 缺少资产/负债/权益合计"))

        if cash_bs is not None and cash_cf is not None:
            diff = abs(cash_bs - cash_cf)
            if diff > 0.01:
                issues.append(ValidationIssue("ERROR", "CASH_RECON_MISMATCH", f"{quarter}: BS 货币资金与 CF 期末现金差异 {diff}"))
        else:
            issues.append(ValidationIssue("WARN", "CASH_RECON_INCOMPLETE", f"{quarter}: 缺少现金勾稽字段"))

    return issues


def validate_metric_definitions(metrics: MetricStore) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    labels = {}
    for point in metrics.all():
        if point.unit not in {UNIT_CNY, UNIT_RATIO}:
            issues.append(ValidationIssue("ERROR", "UNKNOWN_UNIT", f"{point.key}.{point.quarter}: unknown unit {point.unit}"))
        if point.key.endswith(".current") and point.grain != "current":
            issues.append(ValidationIssue("ERROR", "GRAIN_KEY_MISMATCH", f"{point.key}.{point.quarter}: key says current but grain is {point.grain}"))
        if point.key.endswith(".ytd") and point.grain != "ytd":
            issues.append(ValidationIssue("ERROR", "GRAIN_KEY_MISMATCH", f"{point.key}.{point.quarter}: key says ytd but grain is {point.grain}"))
        if point.key.endswith(".ending") and point.grain != "ending":
            issues.append(ValidationIssue("ERROR", "GRAIN_KEY_MISMATCH", f"{point.key}.{point.quarter}: key says ending but grain is {point.grain}"))
        label_key = point.label
        label_signature = (point.grain, point.unit)
        if label_key in labels and labels[label_key] != label_signature:
            issues.append(ValidationIssue("ERROR", "DUPLICATE_LABEL_DIFFERENT_GRAIN", f"{point.label}: duplicated with different grain/unit"))
        labels[label_key] = label_signature
    return issues


def validate_dashboard_rows(rows: Iterable[DashboardRow], metrics: MetricStore) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    seen_labels = set()
    for row in rows:
        if row.label in seen_labels:
            issues.append(ValidationIssue("ERROR", "DASHBOARD_DUPLICATE_ROW", f"Duplicated dashboard row: {row.label}"))
        seen_labels.add(row.label)

        if "环比" in row.label and row.grain != GRAIN_CURRENT:
            issues.append(ValidationIssue("ERROR", "QOQ_NOT_CURRENT", f"{row.label}: 环比 row must use current grain"))
        if "环比" in row.label and "qoq" not in row.metric_key:
            issues.append(ValidationIssue("ERROR", "QOQ_WRONG_METRIC", f"{row.label}: 环比 row must bind to qoq metric"))
        if row.unit == UNIT_CNY and "万元" not in row.label:
            issues.append(ValidationIssue("WARN", "MONEY_ROW_WITHOUT_UNIT_LABEL", f"{row.label}: money row label should mention 万元"))

        for quarter in QUARTERS:
            point = metrics.get(row.metric_key, quarter)
            if point is None:
                continue
            if point.grain != row.grain:
                issues.append(ValidationIssue("ERROR", "DASHBOARD_GRAIN_MISMATCH", f"{row.label}.{quarter}: row grain {row.grain}, metric grain {point.grain}"))
            if point.unit != row.unit:
                issues.append(ValidationIssue("ERROR", "DASHBOARD_UNIT_MISMATCH", f"{row.label}.{quarter}: row unit {row.unit}, metric unit {point.unit}"))
    return issues
