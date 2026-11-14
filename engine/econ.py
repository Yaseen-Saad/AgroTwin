# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Crop economics: profit ranges, barcode classes and legume credits.

The engine remains in hectares, millimetres and EGP. For one replay window (up to three years):

    1 - Y_a / Y_m = K_y * (1 - ET_a / ET_c)
    profit = Y_a * P - (C_seed + C_fert + C_labour + C_water * 10 * I_mm) + N_credit * P_N

``water_use_mm`` is actual transpiration (ET_a) from the replay; the caller must also supply the
window's potential crop ET (``et_c_mm``) so the FAO-33 yield response is not silently skipped.
``variable_cost_egp_per_ha`` is the sum of seed, fertilizer and labour for one crop occurrence.

Every price and cost row in ``data/prices.csv`` carries a year and a source tag. Prices are
constants, never forecasts; ``price_scenario`` is a user-supplied multiplier. Barcode classes use
``assumption:amber_margin`` on the window cost.

Launch-day limitation: per-crop water is not part of the frozen replay window, so the yield
response is applied to the window's total potential revenue with an occurrence-weighted K_y. This
is recorded in ``notes`` rather than hidden.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from statistics import median
from typing import Any

from agrotwin import REPO_ROOT
from engine.config import assumption_value, load_assumptions
from engine.crops import default_catalogue

DEFAULT_PRICES_PATH = REPO_ROOT / "data" / "prices.csv"
WATER_M3_PER_MM_HA = 10.0
SOURCE_TAG = "computed"

_REQUIRED_COLUMNS = {
    "generated_by",
    "crop",
    "year",
    "currency",
    "price_egp_per_t",
    "price_source",
    "yield_max_t_per_ha",
    "yield_source",
    "variable_cost_egp_per_ha",
    "cost_source",
}
_SOURCE_PATTERN = re.compile(r"^(assumption:[a-z0-9_]+|quoted:https?://\S+)$")

CROP_ECONOMICS_COLUMNS = (
    "crop",
    "price_egp_per_t",
    "yield_max_t_per_ha",
    "variable_cost_egp_per_ha",
    "ky",
)


class EconError(ValueError):
    """Raised when a price row or a profit input is incomplete or inconsistent."""


def _check_source(source: str, *, row: str) -> str:
    value = str(source).strip()
    if not _SOURCE_PATTERN.match(value):
        raise EconError(f"{row} source '{value}' must be assumption:<id> or quoted:<url>")
    if value.startswith("assumption:"):
        assumption_id = value.split(":", 1)[1]
        if assumption_id not in load_assumptions():
            raise EconError(
                f"{row} references unknown assumption '{assumption_id}'; "
                "add it to engine/config/assumptions.yaml"
            )
    return value


def _number(value: Any, *, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EconError(f"{field} must be numeric, got {value!r}") from exc
    if number < 0.0:
        raise EconError(f"{field} must be non-negative, got {number}")
    return number


@lru_cache(maxsize=4)
def load_prices(path: str | None = None) -> dict[str, dict[str, Any]]:
    """Load and validate ``data/prices.csv`` keyed by crop id."""
    target = Path(path) if path else DEFAULT_PRICES_PATH
    with target.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise EconError(f"{target} has no header row")
        missing = _REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise EconError(f"{target} is missing columns: {sorted(missing)}")
        rows: dict[str, dict[str, Any]] = {}
        for line_number, raw in enumerate(reader, start=2):
            crop = str(raw["crop"]).strip()
            if not crop or crop in rows:
                raise EconError(f"{target}:{line_number} has a blank or duplicate crop id")
            year = int(raw["year"])
            if not 1981 <= year <= 2100:
                raise EconError(f"{target}:{line_number} year {year} is outside 1981..2100")
            rows[crop] = {
                "crop": crop,
                "year": year,
                "currency": str(raw["currency"]).strip().upper(),
                "price_egp_per_t": _number(
                    raw["price_egp_per_t"], field=f"{crop}.price_egp_per_t"
                ),
                "price_source": _check_source(
                    raw["price_source"], row=f"{crop}.price_egp_per_t"
                ),
                "yield_max_t_per_ha": _number(
                    raw["yield_max_t_per_ha"], field=f"{crop}.yield_max_t_per_ha"
                ),
                "yield_source": _check_source(
                    raw["yield_source"], row=f"{crop}.yield_max_t_per_ha"
                ),
                "variable_cost_egp_per_ha": _number(
                    raw["variable_cost_egp_per_ha"],
                    field=f"{crop}.variable_cost_egp_per_ha",
                ),
                "cost_source": _check_source(
                    raw["cost_source"], row=f"{crop}.variable_cost_egp_per_ha"
                ),
            }
    if not rows:
        raise EconError(f"{target} has no crop rows")
    return rows


def economics_for_rotation(
    rotation: Mapping[str, Any],
    *,
    prices: Mapping[str, Mapping[str, Any]] | None = None,
    catalogue: Any | None = None,
) -> list[dict[str, Any]]:
    """Expand one rotation document into one economics row per planted crop slot."""
    price_rows = prices or load_prices()
    crops = catalogue or default_catalogue()
    slots = rotation.get("slots")
    if not isinstance(slots, list) or not slots:
        raise EconError("rotation must contain a non-empty 'slots' list")
    expanded: list[dict[str, Any]] = []
    for slot in slots:
        crop_id = str(slot["crop"])
        if crop_id == "fallow":
            continue
        row = price_rows.get(crop_id)
        if row is None:
            raise EconError(f"no price row for crop '{crop_id}' in data/prices.csv")
        crop = crops.get(crop_id)
        expanded.append(
            {
                "crop": crop_id,
                "price_egp_per_t": float(row["price_egp_per_t"]),
                "yield_max_t_per_ha": float(row["yield_max_t_per_ha"]),
                "variable_cost_egp_per_ha": float(row["variable_cost_egp_per_ha"]),
                "ky": float(crop.ky),
            }
        )
    if not expanded:
        raise EconError("rotation has no planted crop slots")
    return expanded


def _credit_midpoint(window_metrics: Mapping[str, Any]) -> float:
    credit = window_metrics.get("n_credit_kg_ha")
    if not isinstance(credit, Mapping):
        return 0.0
    low = float(credit.get("low", 0.0))
    high = float(credit.get("high", low))
    return max(0.0, (low + high) / 2.0)


def _profit_with_multiplier(
    *,
    multiplier: float,
    potential_revenue: float,
    yield_ratio: float,
    variable_cost: float,
    water_cost: float,
    n_credit_value: float,
) -> dict[str, Any]:
    profit = potential_revenue * multiplier * yield_ratio - variable_cost - water_cost
    profit += n_credit_value
    return {
        "price_mult": round(multiplier, 6),
        "profit_per_ha": round(profit, 3),
    }


def profit_per_ha(
    *,
    window_metrics: Mapping[str, Any],
    crop_economics: Sequence[Mapping[str, Any]],
    price_scenario: Mapping[str, float],
) -> dict[str, Any]:
    """Return per-hectare profit with low/base/high price scenarios and source tags.

    ``window_metrics`` must include ``water_use_mm`` (ET_a) and ``et_c_mm`` (ET_c). It may also
    include ``irrigation_mm`` and the replay's ``n_credit_kg_ha`` range. ``crop_economics`` is one
    row per planted crop occurrence, normally from :func:`economics_for_rotation`.
    """
    if not crop_economics:
        raise EconError("crop_economics must contain at least one crop")
    try:
        et_a = float(window_metrics["water_use_mm"])
        et_c = float(window_metrics["et_c_mm"])
    except KeyError as exc:
        raise EconError(
            "window_metrics must include water_use_mm and et_c_mm; "
            "et_c_mm comes from the replay details, not the frozen replay window"
        ) from exc
    if et_a < 0.0 or et_c <= 0.0:
        raise EconError("water_use_mm must be >= 0 and et_c_mm must be > 0")

    potential_revenue = 0.0
    variable_cost = 0.0
    weighted_ky = 0.0
    for row in crop_economics:
        missing = [key for key in CROP_ECONOMICS_COLUMNS if key not in row]
        if missing:
            raise EconError(f"crop economics row is missing {missing}")
        yield_max = float(row["yield_max_t_per_ha"])
        price = float(row["price_egp_per_t"])
        revenue = yield_max * price
        potential_revenue += revenue
        variable_cost += float(row["variable_cost_egp_per_ha"])
        weighted_ky += float(row["ky"]) * revenue
    if potential_revenue <= 0.0:
        raise EconError("potential revenue is zero; check yield_max and price rows")
    ky = weighted_ky / potential_revenue

    price_mult = float(price_scenario.get("price_mult", 1.0))
    if not 0.0 <= price_mult <= 5.0:
        raise EconError("price_mult must be within 0..5")
    band = float(price_scenario.get("price_band", assumption_value("price_band")))
    if not 0.0 <= band <= 1.0:
        raise EconError("price_band must be within 0..1")
    n_price = float(
        price_scenario.get("n_price_egp_per_kg", assumption_value("n_price"))
    )
    water_price = float(
        price_scenario.get("water_cost_egp_per_m3", assumption_value("water_cost"))
    )
    irrigation_mm = float(window_metrics.get("irrigation_mm", 0.0))
    if irrigation_mm < 0.0:
        raise EconError("irrigation_mm must be non-negative")

    ratio = 1.0 - ky * (1.0 - et_a / et_c)
    ratio = min(1.0, max(0.0, ratio))
    water_cost = irrigation_mm * WATER_M3_PER_MM_HA * water_price
    n_credit_value = _credit_midpoint(window_metrics) * n_price

    low = price_mult * (1.0 - band)
    high = price_mult * (1.0 + band)
    return {
        "low": _profit_with_multiplier(
            multiplier=low,
            potential_revenue=potential_revenue,
            yield_ratio=ratio,
            variable_cost=variable_cost,
            water_cost=water_cost,
            n_credit_value=n_credit_value,
        ),
        "base": _profit_with_multiplier(
            multiplier=price_mult,
            potential_revenue=potential_revenue,
            yield_ratio=ratio,
            variable_cost=variable_cost,
            water_cost=water_cost,
            n_credit_value=n_credit_value,
        ),
        "high": _profit_with_multiplier(
            multiplier=high,
            potential_revenue=potential_revenue,
            yield_ratio=ratio,
            variable_cost=variable_cost,
            water_cost=water_cost,
            n_credit_value=n_credit_value,
        ),
        "yield_ratio": round(ratio, 6),
        "potential_revenue_egp_per_ha": round(potential_revenue, 3),
        "variable_cost_egp_per_ha": round(variable_cost, 3),
        "water_cost_egp_per_ha": round(water_cost, 3),
        "n_credit_value_egp_per_ha": round(n_credit_value, 3),
        "cost_per_ha": round(variable_cost + water_cost, 3),
        "currency": "EGP",
        "source": SOURCE_TAG,
        "notes": [
            "Profit covers the whole replay window (up to three years), not one annual season.",
            "Prices are constants from data/prices.csv; the multiplier is a user scenario, "
            "not a forecast.",
            "Per-crop water is not in the frozen replay contract, so K_y is occurrence-weighted.",
        ],
    }


def _percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise EconError("percentile needs at least one value")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _range_metric(
    values: Sequence[float], *, unit: str | None = None, currency: str | None = None
) -> dict[str, Any]:
    metric: dict[str, Any] = {
        "p10": round(_percentile(values, 0.10), 3),
        "median": round(float(median(values)), 3),
        "p90": round(_percentile(values, 0.90), 3),
        "source": SOURCE_TAG,
    }
    if unit is not None:
        metric["unit"] = unit
    if currency is not None:
        metric["currency"] = currency
    return metric


def summarize_rotation(
    *,
    rotation: Mapping[str, Any],
    windows: Sequence[Mapping[str, Any]],
    details: Mapping[int, Mapping[str, Any]],
    price_scenario: Mapping[str, float] | None = None,
    prices: Mapping[str, Mapping[str, float]] | None = None,
    amber_margin: float | None = None,
) -> dict[str, Any]:
    """Build the result-schema rotation metrics from replay windows and B-03 inputs.

    Water, erosion, bare days and profit are annualised by dividing the three-year window by
    three, matching ``contracts/fixtures/result.delta_01.json``. The caller adds ``evidence``,
    ``benefits``, ``gaps`` and ``review_flags``; those belong to the API/content layer.
    """
    if not windows:
        raise EconError("windows must contain at least one replay window")
    rotation_id = str(rotation["rotation_id"])
    crop_economics = economics_for_rotation(rotation, prices=prices)
    scenario = dict(price_scenario or {})
    margin = (
        float(amber_margin)
        if amber_margin is not None
        else float(assumption_value("amber_margin"))
    )
    if not 0.0 <= margin <= 1.0:
        raise EconError("amber_margin must be within 0..1")

    lengths = {len(window.get("years", [])) for window in windows}
    lengths.discard(0)
    if len(lengths) > 1:
        raise EconError("all replay windows must cover the same number of years")
    period = lengths.pop() if lengths else 3

    water: list[float] = []
    deficit: list[float] = []
    bare: list[float] = []
    erosion: list[float] = []
    profits: list[float] = []
    costs: list[float] = []
    striped: list[dict[str, Any]] = []
    for window in windows:
        year = int(window["start_year"])
        metrics = details.get(year)
        if metrics is None:
            raise EconError(f"details missing rotation '{rotation_id}' start year {year}")
        profit = profit_per_ha(
            window_metrics=metrics,
            crop_economics=crop_economics,
            price_scenario=scenario,
        )
        annual_profit = float(profit["base"]["profit_per_ha"]) / period
        profits.append(annual_profit)
        costs.append(float(profit["cost_per_ha"]) / period)
        water.append(float(window["water_use_mm"]) / period)
        deficit.append(float(window["deficit_days"]) / period)
        bare.append(float(window["bare_days"]) / period)
        erosion.append(float(window["erosion_index"]) / period)
        striped.append({"year": year, "profit_per_ha": annual_profit})

    code = barcode(windows=striped, cost_per_ha=median(costs), amber_margin=margin)
    credit = windows[0]["n_credit_kg_ha"]
    return {
        "rotation_id": rotation_id,
        "label": str(rotation["label"]),
        "metrics": {
            "water_use_mm": _range_metric(water, unit="mm_per_year"),
            "deficit_days": _range_metric(deficit, unit="days_per_year"),
            "bare_days": _range_metric(bare, unit="days_per_year"),
            "erosion_index": _range_metric(erosion, unit="index_per_year"),
            "n_credit_kg_ha": {
                "low": float(credit["low"]),
                "high": float(credit["high"]),
                "source": str(credit["source"]),
            },
            "profit_per_ha": _range_metric(profits, currency="EGP"),
            "loss_year_share": code["loss_year_share"],
        },
        "barcode": code["stripes"],
        "worst_year": code["worst_year"],
        "loss_year_share": code["loss_year_share"],
        "excluded": {"is_excluded": False, "reasons": []},
    }


def _base_profit(value: Any) -> float:
    if isinstance(value, Mapping):
        base = value.get("base")
        if isinstance(base, Mapping):
            return float(base["profit_per_ha"])
        if "profit_per_ha" in value:
            return float(value["profit_per_ha"])
        raise EconError("profit mapping must contain base.profit_per_ha")
    return float(value)


def barcode(
    *,
    windows: Sequence[Mapping[str, Any]],
    cost_per_ha: float,
    amber_margin: float,
) -> dict[str, Any]:
    """Return barcode stripes, worst year and loss-year share.

    One stripe is emitted per replay window start year. ``cost_per_ha`` is the window's variable
    plus water cost; a positive profit below ``amber_margin * cost_per_ha`` is amber.
    """
    if not windows:
        raise EconError("windows must contain at least one replay window")
    if cost_per_ha < 0.0:
        raise EconError("cost_per_ha must be non-negative")
    if not 0.0 <= amber_margin <= 1.0:
        raise EconError("amber_margin must be within 0..1")
    amber_threshold = amber_margin * cost_per_ha
    stripes: list[dict[str, Any]] = []
    for window in windows:
        year = int(window.get("year", window.get("start_year")))
        profit = _base_profit(window.get("profit_per_ha", window.get("profit")))
        if profit < 0.0:
            loss_class = "red"
        elif profit < amber_threshold:
            loss_class = "amber"
        else:
            loss_class = "green"
        stripes.append(
            {
                "year": year,
                "profit_per_ha": round(profit, 3),
                "currency": "EGP",
                "class": loss_class,
                "source": SOURCE_TAG,
            }
        )
    worst = min(stripes, key=lambda stripe: (stripe["profit_per_ha"], stripe["year"]))
    loss_share = sum(1 for stripe in stripes if stripe["profit_per_ha"] < 0.0) / len(stripes)
    return {
        "stripes": stripes,
        "worst_year": {
            "year": worst["year"],
            "profit_per_ha": worst["profit_per_ha"],
            "currency": "EGP",
            "source": SOURCE_TAG,
        },
        "loss_year_share": {"value": round(loss_share, 6), "source": SOURCE_TAG},
        "cost_per_ha": round(cost_per_ha, 3),
        "amber_threshold_egp_per_ha": round(amber_threshold, 3),
        "amber_margin": amber_margin,
        "source": SOURCE_TAG,
    }
