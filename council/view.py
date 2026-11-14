# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Read-only views of a result document used by advisors and the Field Card."""

from __future__ import annotations

from typing import Any

from .text import fmt_number, fmt_trimmed, label, load_content, unit_label


def top_rotation(result: dict[str, Any]) -> dict[str, Any]:
    """Choose the first non-excluded rotation in the server ranking, with a safe fallback."""
    rotations = result.get("rotations") or []
    by_id = {rotation.get("rotation_id"): rotation for rotation in rotations}
    for rotation_id in result.get("ranking", {}).get("order", []):
        rotation = by_id.get(rotation_id)
        if rotation and not rotation.get("excluded", {}).get("is_excluded"):
            return rotation
    for rotation in rotations:
        if not rotation.get("excluded", {}).get("is_excluded"):
            return rotation
    if not rotations:
        raise ValueError("result has no rotations")
    return rotations[0]


def rotation_label(result: dict[str, Any], rotation: dict[str, Any], language: str) -> str:
    """Localize a rotation label, falling back to the label carried by the result."""
    rotation_id = str(rotation.get("rotation_id", ""))
    configured = load_content("labels").get("rotation", {}).get(rotation_id, {})
    return str(configured.get(language) or rotation.get("label") or rotation_id)


def blindspot_titles(language: str, limit: int = 2) -> str:
    """Return a short localized list of local-review items for a compact card."""
    key = "title_ar" if language == "ar" else "title_en"
    items = load_content("blindspots").get("blindspots", [])[:limit]
    separator = "، " if language == "ar" else ", "
    return separator.join(str(item[key]) for item in items)


def template_values(result: dict[str, Any], language: str) -> dict[str, str]:
    """Build the complete placeholder set from the result; no number is invented here."""
    rotation = top_rotation(result)
    metrics = rotation["metrics"]
    profit = metrics["profit_per_ha"]
    water = metrics["water_use_mm"]
    deficit = metrics["deficit_days"]
    nitrogen = metrics["n_credit_kg_ha"]
    loss = metrics["loss_year_share"]["value"]
    worst = rotation["worst_year"]
    fusion = result["fusion"]
    band_unit = fusion["range_width"]["unit"]
    band_unit_ar = unit_label(band_unit, "ar")
    band_unit_en = unit_label(band_unit, "en")
    used = bool(fusion.get("used"))

    values: dict[str, str] = {
        "site": str(result["site_id"]),
        "mode": label("mode", str(result["mode"]), language),
        "rotation": rotation_label(result, rotation, language),
        "p10": fmt_number(profit["p10"]),
        "median": fmt_number(profit["median"]),
        "p90": fmt_number(profit["p90"]),
        "currency": str(profit.get("currency") or "EGP"),
        "w10": fmt_number(water["p10"]),
        "w90": fmt_number(water["p90"]),
        "def10": fmt_number(deficit["p10"]),
        "def90": fmt_number(deficit["p90"]),
        "n_low": fmt_number(nitrogen["low"]),
        "n_high": fmt_number(nitrogen["high"]),
        "n_source": str(nitrogen["source"]),
        "loss_pct": fmt_trimmed(loss * 100, 1),
        "year": str(worst["year"]),
        "profit": fmt_number(worst["profit_per_ha"]),
        "years": str(len(result.get("years", []))),
        "points": fmt_number(fusion.get("n_points", 0)),
        "ess": fmt_number(fusion.get("ess", 0), 1) if used else "0",
        "without": fmt_number(fusion["range_width"]["without_scout"]),
        "with": fmt_number(fusion["range_width"]["with_scout"]) if used else fmt_number(
            fusion["range_width"]["without_scout"]
        ),
        "band_unit": band_unit_en,
        "band_unit_ar": band_unit_ar,
        "blindspots": blindspot_titles(language, 2),
    }
    return values
