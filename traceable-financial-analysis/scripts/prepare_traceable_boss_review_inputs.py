#!/usr/bin/env python3
"""
prepare_traceable_boss_review_inputs.py — FinClaw-specific example helper.

This script belongs to traceable-financial-analysis, not maybeai-formula-report,
because it encodes business-shaped assumptions:

- Kingdee 3-statement quarterly inputs
- FinClaw raw 12-sheet normalization
- FinClaw 9-sheet boss-review downstream usage

It reads the statement xlsx files and emits normalized raw-sheet payloads that
can later be written into MaybeAI Sheet by the generic traceable-formula layer.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _col_letter_to_index(letter: str) -> int:
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch.upper()) - ord("A") + 1)
    return n


def read_xlsx(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        try:
            with z.open("xl/sharedStrings.xml") as f:
                tree = ET.parse(f)
                for si in tree.getroot().findall("s:si", NS):
                    text_parts = []
                    for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"):
                        text_parts.append(t.text or "")
                    shared.append("".join(text_parts))
        except KeyError:
            pass

        sheet_path = None
        with z.open("xl/workbook.xml") as f:
            tree = ET.parse(f)
            for sheet in tree.getroot().findall("s:sheets/s:sheet", NS):
                if sheet.get("name") in ("利润表", "资产负债表", "现金流量表", "Sheet1"):
                    sheet_path = f"xl/worksheets/sheet{sheet.get('sheetId')}.xml"
                    break
        if sheet_path is None:
            sheet_path = "xl/worksheets/sheet1.xml"

        with z.open(sheet_path) as f:
            tree = ET.parse(f)
            rows_data: dict[int, dict[int, str]] = {}
            max_col = 0
            for row in tree.getroot().iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                r = int(row.get("r"))
                row_cells: dict[int, str] = {}
                for c in row.findall("s:c", NS):
                    ref = c.get("r") or ""
                    cell_type = c.get("t", "n")
                    v_elem = c.find("s:v", NS)
                    inline = c.find("s:is/s:t", NS)
                    if v_elem is not None and v_elem.text is not None:
                        val = v_elem.text
                        if cell_type == "s" and val.isdigit():
                            val = shared[int(val)]
                    elif inline is not None and inline.text is not None:
                        val = inline.text
                    else:
                        val = ""
                    col_letter = "".join(ch for ch in ref if ch.isalpha())
                    col_idx = _col_letter_to_index(col_letter)
                    row_cells[col_idx] = val
                    max_col = max(max_col, col_idx)
                rows_data[r] = row_cells

            if not rows_data:
                return []
            max_row = max(rows_data.keys())
            return [
                [rows_data.get(r, {}).get(c, "") for c in range(1, max_col + 1)]
                for r in range(1, max_row + 1)
            ]


def normalize_statement(values: list[list[str]], statement: str, company: str) -> list[list[str]]:
    if not values:
        return []
    header = [
        "项目",
        "行次",
        "本年累计金额" if statement == "利润表" else ("期末余额" if statement == "资产负债表" else "本期金额"),
        "本期金额" if statement != "资产负债表" else "年初余额",
    ]
    result = [
        [statement, "", "", ""],
        [f"编制单位：{company}", "", "", ""],
        header,
    ]
    for row in values:
        if not row or not row[0].strip():
            continue
        if row[0].strip() in ("项目", "一、", "二、", "三、", "四、"):
            continue
        padded = (row + ["", "", "", ""])[:4]
        result.append([str(v) if v is not None else "" for v in padded])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare FinClaw traceable boss-review raw-sheet payloads.")
    parser.add_argument("--input-dir", required=True, help="Directory containing quarterly statement xlsx files.")
    parser.add_argument("--company", required=True, help="Company name used in normalized sheet headers.")
    parser.add_argument("--period", required=True, help="Period label, for example 2025.")
    parser.add_argument("--output-json", default="/tmp/finclaw_traceable_raw.json", help="JSON file to write.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    raw_sheets: dict[str, list[list[str]]] = {}

    for statement, prefix in [
        ("利润表", "利润表"),
        ("资产负债表", "资产负债表"),
        ("现金流量表", "现金流量表"),
    ]:
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            xlsx_path = input_dir / f"{prefix}-{args.period}{quarter}.xlsx"
            if not xlsx_path.exists():
                print(f"WARNING missing file: {xlsx_path}")
                continue
            values = read_xlsx(xlsx_path)
            normalized = normalize_statement(values, statement, args.company)
            raw_sheets[f"{statement}-{args.period}{quarter}"] = normalized

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(raw_sheets, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
