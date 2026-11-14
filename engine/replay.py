# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Historical-analog replay orchestration.

A replay window starts in historical year ``y`` and runs the rotation's three years on the
actual weather of ``y``, ``y+1`` and ``y+2`` so multi-year droughts stay intact. Start years run
from the first cached year to the last cached year minus two.

Crop timing is deterministic:

- A slot's calendar year is ``start_year + slot.year - 1``.
- A crop is planted at the midpoint of its catalogue planting window in that calendar year
  (``engine/crops.yaml``). Winter crops therefore start in autumn and may cross into the next
  calendar year; summer crops start in spring.
- Growth lasts ``sum(stages_days)`` days. Days outside ``[y-01-01, (y+2)-12-31]`` are clipped.
- If two crops cover the same day, the earlier-planted crop keeps the day (a standing crop owns
  the land).

The weather columns are typed once and ET0 is precomputed once per site and scenario, then each
window is a slice. That keeps three rotations over every historical start year inside the
two-second budget.

Output validates against ``contracts/replay.schema.json``. All values are ``computed``; a
historical replay is not a forecast.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Mapping, Sequence
from datetime import date, timedelta
from typing import Any

from engine.config import assumption_value
from engine.crops import Crop, CropCatalog, default_catalogue
from engine.soil import get_soil_class
from engine.waterbalance import (
    balance_metrics,
    et0_series,
    prepare_weather,
    window_from_metrics,
)

GENERATED_BY = (
    "agent-B / opencode/big-pickle / 2026-11-14 "
    "(engine.replay; FAO-56 balance on NASA POWER daily weather)"
)
MODES = {"LIVE", "REPLAY", "SIMULATED", "NONE"}
SCENARIO_KEYS = ("rain_mult", "temp_offset_c", "price_mult")


class ReplayError(ValueError):
    """Raised when the input cannot produce a contract-valid replay."""


def _month_day(value: str) -> tuple[int, int]:
    month, _, day = value.partition("-")
    return int(month), int(day)


def planting_date(crop: Crop, calendar_year: int) -> date:
    """Return the deterministic planting date for a crop in a calendar year."""
    window = crop.planting_window
    if window is not None:
        start_month, start_day = _month_day(window["start"])
        end_month, end_day = _month_day(window["end"])
        start = date(calendar_year, start_month, start_day)
        end = date(calendar_year, end_month, end_day)
        if end < start:
            end = date(calendar_year + 1, end_month, end_day)
        return start + timedelta(days=(end - start).days // 2)
    if crop.season == "winter":
        return date(calendar_year, 10, 1)
    if crop.season == "summer":
        return date(calendar_year, 6, 1)
    return date(calendar_year, 1, 1)


def rotation_schedule(
    rotation: Mapping[str, Any],
    catalogue: CropCatalog,
    *,
    start_year: int,
    window_start: date,
    window_end: date,
) -> dict[date, tuple[Crop, int]]:
    """Map every crop day inside the window to ``(crop, day_index_since_planting)``."""
    schedule: dict[date, tuple[Crop, int]] = {}
    planted_on: dict[date, date] = {}
    for slot in rotation["slots"]:
        crop = catalogue.get(str(slot["crop"]))
        if crop.crop_id == "fallow":
            continue
        calendar_year = start_year + int(slot["year"]) - 1
        planted = planting_date(crop, calendar_year)
        for offset in range(crop.total_days):
            day = planted + timedelta(days=offset)
            if day < window_start or day > window_end:
                continue
            existing = schedule.get(day)
            if existing is None or planted < planted_on[day]:
                schedule[day] = (crop, offset)
                planted_on[day] = planted
    return schedule


def _weather_rows(site: Mapping[str, Any]) -> list[dict[str, Any]]:
    daily = site.get("daily")
    if not isinstance(daily, Mapping):
        raise ReplayError("site document is missing the daily block")
    columns = list(daily.get("columns", []))
    if "date" not in columns:
        raise ReplayError("site daily block is missing the date column")
    rows: list[dict[str, Any]] = []
    for raw in daily.get("rows", []):
        if len(raw) != len(columns):
            raise ReplayError("site daily row width does not match columns")
        row = dict(zip(columns, raw, strict=True))
        raw_date = row.get("date")
        if isinstance(raw_date, date):
            pass
        elif isinstance(raw_date, str):
            row["date"] = date.fromisoformat(raw_date)
        else:
            raise ReplayError("site daily rows need ISO date strings")
        rows.append(row)
    rows.sort(key=lambda row: row["date"])
    if not rows:
        raise ReplayError("site daily block has no rows")
    return rows


def _validate_scenario(scenario: Mapping[str, float]) -> dict[str, float]:
    missing = [key for key in SCENARIO_KEYS if key not in scenario]
    if missing:
        raise ReplayError(f"scenario is missing {missing}")
    values = {key: float(scenario[key]) for key in SCENARIO_KEYS}
    if not 0.0 <= values["rain_mult"] <= 3.0:
        raise ReplayError("scenario.rain_mult must be within 0..3")
    if not -10.0 <= values["temp_offset_c"] <= 10.0:
        raise ReplayError("scenario.temp_offset_c must be within -10..10")
    if not 0.0 <= values["price_mult"] <= 5.0:
        raise ReplayError("scenario.price_mult must be within 0..5")
    return values


def run_replay(
    site: Mapping[str, Any],
    rotations: Sequence[Mapping[str, Any]],
    scenario: Mapping[str, float],
    *,
    irrigation_log: Mapping[str, float] | None = None,
    mode: str = "NONE",
    catalogue: CropCatalog | None = None,
    with_details: bool = False,
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, dict[int, dict[str, Any]]]]:
    """Replay every historical start year for every rotation.

    Args:
        site: A document valid against ``contracts/site.schema.json``.
        rotations: Documents valid against ``contracts/rotation.schema.json``.
        scenario: ``rain_mult``, ``temp_offset_c`` and ``price_mult``.
        irrigation_log: Date -> gross millimetres for irrigated sites.
        mode: ``LIVE``, ``REPLAY``, ``SIMULATED`` or ``NONE`` (no Scout data).
        catalogue: Optional crop catalogue, mainly for tests.
        with_details: Also return per-window ET_c and cost inputs for ``engine.econ``. The
            replay document itself stays schema-valid; the details never enter the contract.

    Returns:
        A document valid against ``contracts/replay.schema.json``; when ``with_details`` is
        true, a ``(document, details)`` pair where details map rotation id -> start year ->
        economics inputs.
    """
    if mode not in MODES:
        raise ReplayError(f"mode must be one of {sorted(MODES)}")
    if not rotations:
        raise ReplayError("at least one rotation is required")
    scenario_values = _validate_scenario(scenario)
    catalogue = catalogue or default_catalogue()

    rows = _weather_rows(site)
    prepared = prepare_weather(
        rows,
        rain_mult=scenario_values["rain_mult"],
        temp_offset_c=scenario_values["temp_offset_c"],
    )
    dates = prepared.days
    first_year = dates[0].year
    last_year = dates[-1].year
    start_years = list(range(first_year, last_year - 1))
    if not start_years:
        raise ReplayError("the cache needs at least three calendar years for one window")

    lat = float(site["lat"])
    elevation = float(site.get("elevation_m") or 0.0)
    et0_values = et0_series(prepared, lat_deg=lat, elevation_m=elevation)

    site_id = str(site.get("site_id", ""))
    soil_class = str(site.get("soil_class", ""))
    if not soil_class:
        raise ReplayError("site document needs a soil_class for the water balance")
    irrigated = str(site.get("irrigation", "rainfed")) == "irrigated"
    soil_awc = get_soil_class(soil_class).available_water_fraction
    irrigation_efficiency = float(assumption_value("irrigation_efficiency"))
    if not 0.0 < irrigation_efficiency <= 1.0:
        raise ReplayError("assumption:irrigation_efficiency must be within (0, 1]")
    heavy_rain_mm = float(assumption_value("heavy_rain_mm"))

    rotation_blocks: list[dict[str, Any]] = []
    details: dict[str, dict[int, dict[str, Any]]] = {}
    for rotation in rotations:
        rotation_id = str(rotation["rotation_id"])
        label = str(rotation["label"])
        windows: list[dict[str, Any]] = []
        for start_year in start_years:
            window_start = date(start_year, 1, 1)
            window_end = date(start_year + 2, 12, 31)
            schedule = rotation_schedule(
                rotation,
                catalogue,
                start_year=start_year,
                window_start=window_start,
                window_end=window_end,
            )
            lo = bisect_left(dates, window_start)
            hi = bisect_right(dates, window_end)
            if hi <= lo:
                continue
            metrics = balance_metrics(
                prepared.slice(lo, hi),
                schedule,
                et0_values=et0_values[lo:hi],
                soil_awc=soil_awc,
                irrigated=irrigated,
                irrigation_efficiency=irrigation_efficiency,
                heavy_rain_mm=heavy_rain_mm,
                irrigation_log=irrigation_log,
            )
            windows.append(window_from_metrics(metrics, start_year=start_year))
            details.setdefault(rotation_id, {})[start_year] = {
                "water_use_mm": metrics["water_use_mm"],
                "et_c_mm": metrics["et_c_mm"],
                "irrigation_mm": metrics["irrigation_mm"],
                "n_credit_kg_ha": metrics["n_credit_kg_ha"],
                "stress_days": metrics["stress_days"],
                "deficit_days": metrics["deficit_days"],
            }
        if not windows:
            raise ReplayError(f"rotation '{rotation_id}' produced no windows")
        rotation_blocks.append(
            {"rotation_id": rotation_id, "label": label, "windows": windows}
        )

    document = {
        "site_id": site_id,
        "generated_by": GENERATED_BY,
        "mode": mode,
        "years": start_years,
        "scenario": scenario_values,
        "rotations": rotation_blocks,
    }
    if with_details:
        return document, details
    return document
