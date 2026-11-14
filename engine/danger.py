# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Robust danger-window detection for the field diagnosis timeline.

For every day-of-year and variable (rainfall and maximum temperature from the cached NASA POWER
rows) compute a day-of-year baseline median and MAD across all cached years, using a circular
window of ``assumption:danger_window_days`` days on each side:

    z_d = (x_d - median_d) / (1.4826 * MAD_d)

Flag a window when ``abs(z) > assumption:danger_z`` for at least ``assumption:danger_min_days``
consecutive days. Runs may cross calendar years because the series is chronological, not
year-by-year.

Feb 29 is folded into Dec 31 (one 365-day circle) so the baseline is defined every year. If a
baseline window has zero MAD, the mean absolute deviation is used; if that is also zero the
z-score is zero, so a perfectly constant series never raises a false alarm.

Modelled wetness and cached NDVI are named in the Agent guide but are not present in the site
cache (``monthly_ndvi`` is monthly and often null), so they are deliberately skipped rather than
invented. Output windows are ``computed``; this is a historical diagnostic, not a forecast.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from statistics import median
from typing import Any

from engine.config import assumption_value

DANGER_VARIABLES = ("precip_mm", "tmax_c")
SOURCE_TAG = "computed"
EPSILON = 1e-9
CIRCLE_DAYS = 365


@dataclass(frozen=True)
class _Point:
    day: date
    circle_day: int
    value: float


def _circle_day(day: date) -> int:
    doy = day.timetuple().tm_yday
    return CIRCLE_DAYS if doy == 366 else doy


def _series(site: Mapping[str, Any], variable: str) -> list[_Point]:
    daily = site.get("daily")
    if not isinstance(daily, Mapping):
        return []
    columns = list(daily.get("columns", []))
    if "date" not in columns or variable not in columns:
        return []
    date_index = columns.index("date")
    value_index = columns.index(variable)
    points: list[_Point] = []
    for row in daily.get("rows", []):
        raw = row[value_index]
        if raw is None or isinstance(raw, bool) or not isinstance(raw, (int, float)):
            continue
        day = date.fromisoformat(str(row[date_index]))
        points.append(_Point(day, _circle_day(day), float(raw)))
    points.sort(key=lambda point: point.day)
    return points


def _baselines(
    points: Sequence[_Point], half_width: int
) -> dict[int, tuple[float, float]]:
    buckets: dict[int, list[float]] = {}
    for point in points:
        buckets.setdefault(point.circle_day, []).append(point.value)

    baselines: dict[int, tuple[float, float]] = {}
    for circle_day in range(1, CIRCLE_DAYS + 1):
        values: list[float] = []
        for offset in range(-half_width, half_width + 1):
            neighbour = ((circle_day - 1 + offset) % CIRCLE_DAYS) + 1
            values.extend(buckets.get(neighbour, ()))
        if not values:
            continue
        centre = median(values)
        mad = median(abs(value - centre) for value in values)
        scale = 1.4826 * mad
        if scale <= EPSILON:
            mean_absolute_deviation = sum(abs(value - centre) for value in values) / len(values)
            scale = 1.2533 * mean_absolute_deviation
        baselines[circle_day] = (centre, scale)
    return baselines


def _window(
    variable: str, run: Sequence[tuple[_Point, float]]
) -> dict[str, Any]:
    peak_point, peak_z = max(run, key=lambda pair: abs(pair[1]))
    return {
        "variable": variable,
        "start_date": run[0][0].day.isoformat(),
        "end_date": run[-1][0].day.isoformat(),
        "days": len(run),
        "peak_z": round(peak_z, 3),
        "peak_date": peak_point.day.isoformat(),
        "source": SOURCE_TAG,
    }


def _detect(
    variable: str,
    points: Sequence[_Point],
    baselines: Mapping[int, tuple[float, float]],
    *,
    threshold_z: float,
    min_days: int,
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    run: list[tuple[_Point, float]] = []
    for point in points:
        centre, scale = baselines.get(point.circle_day, (None, 0.0))
        if centre is None or scale <= EPSILON:
            z_score = 0.0
        else:
            z_score = (point.value - centre) / scale
        if abs(z_score) > threshold_z:
            run.append((point, z_score))
            continue
        if len(run) >= min_days:
            windows.append(_window(variable, run))
        run = []
    if len(run) >= min_days:
        windows.append(_window(variable, run))
    return windows


def danger_windows(site: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return flagged danger windows with variable, date range, peak z-score and source tag."""
    threshold_z = float(assumption_value("danger_z"))
    min_days = int(assumption_value("danger_min_days"))
    half_width = int(assumption_value("danger_window_days"))
    if threshold_z <= 0.0:
        raise ValueError("assumption:danger_z must be positive")
    if min_days < 1:
        raise ValueError("assumption:danger_min_days must be at least 1")
    if half_width < 1 or half_width >= CIRCLE_DAYS // 2:
        raise ValueError("assumption:danger_window_days must be within 1..182")

    windows: list[dict[str, Any]] = []
    for variable in DANGER_VARIABLES:
        points = _series(site, variable)
        if not points:
            continue
        baselines = _baselines(points, half_width)
        windows.extend(
            _detect(
                variable,
                points,
                baselines,
                threshold_z=threshold_z,
                min_days=min_days,
            )
        )
    windows.sort(key=lambda window: (window["start_date"], window["variable"]))
    return windows
