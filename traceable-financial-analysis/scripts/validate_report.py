#!/usr/bin/env python3
"""Validate FinClaw three-statement inputs and metric consistency."""

from __future__ import annotations

import argparse
import json
import sys

from finclaw_report_core.consistency_checks import validate_all
from finclaw_report_core.dashboard_rows import build_dashboard_rows
from finclaw_report_core.metrics import build_metrics
from finclaw_report_core.statement_facts import parse_statement_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate statement parsing, metric-grain, unit, and dashboard consistency.")
    parser.add_argument("--input-dir", required=True, help="Directory containing statement xlsx files.")
    parser.add_argument("--company", default="", help="Company name override.")
    parser.add_argument("--year", type=int, default=None, help="Report year override.")
    parser.add_argument("--source-basis", default="FIN_STMT", choices=["FIN_STMT", "SYNTHETIC_DEMO"], help="Source basis label.")
    args = parser.parse_args(argv)

    facts = parse_statement_directory(args.input_dir, company=args.company, year=args.year)
    metrics = build_metrics(facts, source_basis=args.source_basis)
    dashboard_rows = build_dashboard_rows(metrics)
    validation = validate_all(facts, metrics, dashboard_rows)

    print(json.dumps({"passed": validation.passed, "issues": [issue.__dict__ for issue in validation.issues]}, ensure_ascii=False, indent=2))
    return 0 if validation.passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
