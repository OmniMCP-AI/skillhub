#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = "https://play-be.omnimcp.ai/api/v1/excel"


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return [row for row in reader]


def post_json(path: str, payload: dict, token: str) -> dict:
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_sheet_name(name: str) -> str:
    invalid = set("[]:*?/\\")
    cleaned = "".join("_" if ch in invalid else ch for ch in name).strip()
    return cleaned[:31] or "Sheet1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export BI summary CSVs to Maybe Sheet.")
    parser.add_argument("--summary-csv", required=True, type=Path, help="Primary summary CSV to create workbook from.")
    parser.add_argument("--extra-csv", action="append", default=[], type=Path, help="Additional CSVs to write as new worksheets.")
    parser.add_argument("--workbook-name", default="bi-analysis-output", help="Workbook/sheet base name.")
    parser.add_argument("--summary-sheet-name", default="BI_Summary", help="Worksheet name for the primary summary CSV.")
    parser.add_argument("--write-result", type=Path, help="Optional JSON file to save API result metadata.")
    args = parser.parse_args()

    token = os.environ.get("MAYBEAI_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("Missing MAYBEAI_API_TOKEN")

    summary_rows = read_csv_rows(args.summary_csv)
    if not summary_rows:
        raise SystemExit(f"Summary CSV is empty: {args.summary_csv}")

    header = summary_rows[0]
    data_rows = summary_rows[1:]
    primary_data = [dict(zip(header, row)) for row in data_rows]
    if not primary_data:
        primary_data = [dict(zip(header, [""] * len(header)))]

    create_resp = post_json(
        "/write_new_sheet",
        {
            "sheet_name": safe_sheet_name(args.summary_sheet_name),
            "data": primary_data,
        },
        token,
    )
    spreadsheet_url = create_resp.get("spreadsheet_url", "")
    spreadsheet_id = create_resp.get("spreadsheet_id", "")
    file_uri = f"https://www.maybe.ai/docs/spreadsheets/d/{spreadsheet_id}" if spreadsheet_id else spreadsheet_url

    worksheet_results: list[dict[str, str]] = [
        {
            "worksheet_name": safe_sheet_name(args.summary_sheet_name),
            "worksheet_url": spreadsheet_url,
            "source_csv": str(args.summary_csv),
        }
    ]

    for extra_csv in args.extra_csv:
        rows = read_csv_rows(extra_csv)
        if not rows:
            continue
        worksheet_name = safe_sheet_name(extra_csv.stem)
        resp = post_json(
            "/write_new_worksheet",
            {
                "uri": file_uri,
                "worksheet_name": worksheet_name,
                "values": rows,
            },
            token,
        )
        worksheet_results.append(
            {
                "worksheet_name": worksheet_name,
                "worksheet_url": resp.get("spreadsheet_url", ""),
                "source_csv": str(extra_csv),
            }
        )

    result = {
        "success": True,
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": file_uri,
        "worksheets": worksheet_results,
        "message": "Maybe Sheet export completed",
    }

    if args.write_result:
        args.write_result.parent.mkdir(parents=True, exist_ok=True)
        args.write_result.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
