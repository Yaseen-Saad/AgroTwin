# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Bilingual content loading and safe template formatting for Council outputs."""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
PLACEHOLDER = re.compile(r"\{([a-z][a-z0-9_]*)\}")


@cache
def load_content(name: str) -> dict[str, Any]:
    """Load one bilingual content JSON file by stem; paths resolve from the repository root."""
    path = CONTENT_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def label(group: str, key: str, language: str, fallback: str | None = None) -> str:
    """Return a bilingual label, falling back to the key only when the caller allows it."""
    labels = load_content("labels").get(group, {})
    entry = labels.get(key, {})
    value = entry.get(language)
    if value:
        return str(value)
    if fallback is not None:
        return fallback
    return key


def format_template(template: str, values: dict[str, Any]) -> str:
    """Fill ``{name}`` placeholders without evaluating expressions or formatting fields."""

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"template placeholder has no value: {key}")
        return str(values[key])

    return PLACEHOLDER.sub(replace, template)


def fmt_number(value: float | int, decimals: int = 0) -> str:
    """Format a finite number with Western digits and comma grouping for both languages."""
    return f"{float(value):,.{decimals}f}"


def fmt_trimmed(value: float | int, decimals: int = 1) -> str:
    """Format a number and remove trailing zeros, so 25.0 becomes 25."""
    text = fmt_number(value, decimals)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def normalize_unit(unit: str | None) -> str | None:
    """Map contract and display units to the small vocabulary used by the Number Auditor."""
    if not unit:
        return None
    text = unit.strip().lower().replace("_", " ")
    text = " ".join(text.replace("/", " / ").split())
    text = " ".join(text.replace(" per ", " / ").split())
    text = text.replace(" ", "")
    aliases = {
        "mm": "mm",
        "mm/yr": "mm",
        "mm/year": "mm",
        "مم": "mm",
        "مم/سنة": "mm",
        "مم/عام": "mm",
        "egp": "EGP",
        "egp/ha": "EGP",
        "جنيه": "EGP",
        "جنيه/هكتار": "EGP",
        "usd": "USD",
        "usd/ha": "USD",
        "kgn/ha": "kgN/ha",
        "kg/ha": "kgN/ha",
        "كغن/هكتار": "kgN/ha",
        "%": "%",
        "percent": "%",
        "٪": "%",
        "day": "day",
        "days": "day",
        "day/yr": "day",
        "day/year": "day",
        "days/yr": "day",
        "days/year": "day",
        "يوم": "day",
        "أيام": "day",
        "year": "year",
        "years": "year",
        "سنة": "year",
        "سنوات": "year",
        "ha": "ha",
        "hectare": "ha",
        "هكتار": "ha",
        "feddan": "feddan",
        "فدان": "feddan",
        "index": "index",
        "مؤشر": "index",
        "weight": "weight",
        "point": "point",
        "count": "count",
    }
    return aliases.get(text, text)


def unit_label(unit: str | None, language: str) -> str:
    """Return a localized display unit; unknown units keep their contract spelling."""
    if not unit:
        return ""
    entry = load_content("labels").get("unit", {}).get(unit, {})
    value = entry.get(language)
    if value:
        return str(value)
    return unit.replace("_", "/")
