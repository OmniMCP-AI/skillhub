#!/usr/bin/env python3
"""Build a local FinClaw boss-review workbook from a statement directory.

This script is review-ready but not wired into the default Hermes production
flow yet.  It exists so future runs can call stable code instead of generating
temporary parsing/writer scripts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from finclaw_report_core.boss_review_workbook import write_boss_review_workbook
from finclaw_report_core.consistency_checks import validate_all
from finclaw_report_core.dashboard_rows import build_dashboard_rows
from finclaw_report_core.metrics import build_metrics
from finclaw_report_core.statement_facts import parse_statement_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a FinClaw boss-review workbook from three-statement Excel files.")
    parser.add_argument("--input-dir", required=True, help="Directory containing the statement xlsx files.")
    parser.add_argument("--output-xlsx", required=True, help="Workbook path to write.")
    parser.add_argument("--company", default="", help="Company name override.")
    parser.add_argument("--year", type=int, default=None, help="Report year override.")
    parser.add_argument("--source-basis", default="FIN_STMT", choices=["FIN_STMT", "SYNTHETIC_DEMO"], help="Source basis label for metrics.")
    parser.add_argument("--validation-json", default="", help="Optional path for validation details.")
    args = parser.parse_args(argv)

    facts = parse_statement_directory(args.input_dir, company=args.company, year=args.year)
    metrics = build_metrics(facts, source_basis=args.source_basis)
    dashboard_rows = build_dashboard_rows(metrics)
    validation = validate_all(facts, metrics, dashboard_rows)

    if args.validation_json:
        _write_validation_json(Path(args.validation_json), validation)

    validation.raise_for_errors()
    output = write_boss_review_workbook(
        args.output_xlsx,
        facts=facts,
        metrics=metrics,
        dashboard_rows=dashboard_rows,
        validation_issues=validation.issues,
    )
    print(output)
    return 0


def _write_validation_json(path: Path, validation) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "passed": validation.passed,
        "issues": [issue.__dict__ for issue in validation.issues],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
