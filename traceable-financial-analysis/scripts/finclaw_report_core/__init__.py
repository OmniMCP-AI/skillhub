"""Deterministic helpers for FinClaw report generation.

This package is intentionally small and dependency-light.  It gives Hermes a
stable place for statement parsing, normalized metric construction, dashboard
rows, narrative values, and consistency checks so production runs do not
recreate those rules in temporary scripts.
"""

from .dashboard_rows import DashboardRow, build_dashboard_rows
from .metrics import MetricPoint, MetricStore, build_metrics
from .statement_facts import ReportFacts, parse_statement_directory

__all__ = [
    "DashboardRow",
    "MetricPoint",
    "MetricStore",
    "ReportFacts",
    "build_dashboard_rows",
    "build_metrics",
    "parse_statement_directory",
]
