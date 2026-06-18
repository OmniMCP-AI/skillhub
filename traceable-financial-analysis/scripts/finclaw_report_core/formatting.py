"""Shared formatting helpers for report outputs."""

from __future__ import annotations

from typing import Optional


def yuan_to_wan(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return value / 10000.0


def fmt_wan(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{yuan_to_wan(value):.{digits}f}"


def fmt_yuan_as_wan(value: Optional[float], digits: int = 2) -> str:
    return fmt_wan(value, digits=digits)


def fmt_ratio(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.{digits}f}%"


def safe_div(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den in (None, 0):
        return None
    return num / den


def compact_number(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")
