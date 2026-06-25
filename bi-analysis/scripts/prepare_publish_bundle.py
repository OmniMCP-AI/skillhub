#!/usr/bin/env python3
"""Prepare a clean SkillHub publish bundle for bi-analysis."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    include_files = [
        "SKILL.md",
        "README.md",
        "TESTING.md",
        "references/downstream-style-system.md",
        "references/industry-mock-test-matrix.md",
        "references/tableau-inspired-dimensions.md",
        "scripts/export_to_maybe_sheet.py",
        "scripts/prepare_publish_bundle.py",
        "scripts/run_industry_mock_regression.py",
        "scripts/run_llm_usage_regression.py",
        "scripts/run_maybe_workbook_bi.py",
    ]

    for relative in include_files:
        src = source_dir / relative
        dst = output_dir / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    print(output_dir)


if __name__ == "__main__":
    main()
