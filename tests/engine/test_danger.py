# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Robust day-of-year detection flags a planted heat anomaly and nothing else."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from engine.danger import danger_windows


def danger_site(years: range = range(2000, 2020)) -> dict[str, Any]:
    columns = [
        "date",
        "tmean_c",
        "tmin_c",
        "tmax_c",
        "precip_mm",
        "rh_pct",
        "wind_ms",
        "solar_mj_m2",
    ]
    rows = []
    for year in years:
        for day_of_year in range(1, 366):
            day = date(year, 1, 1) + timedelta(days=day_of_year - 1)
            seasonal = 30.0 + 6.0 * math.sin(2.0 * math.pi * (day_of_year - 60) / 365.0)
            noise = ((year * 7 + day_of_year * 13) % 11 - 5) * 0.4
            tmax = seasonal + noise
            if year == 2010 and 180 <= day_of_year <= 186:
                tmax += 12.0
            rows.append(
                [
                    day.isoformat(),
                    tmax - 5.0,
                    tmax - 10.0,
                    tmax,
                    2.0,
                    50.0,
                    2.0,
                    20.0,
                ]
            )
    return {
        "site_id": "danger_site",
        "name": "Synthetic danger site",
        "lat": 31.0,
        "lon": 31.0,
        "generated_by": "test",
        "daily": {
            "source": "nasa:POWER synthetic test fixture",
            "start": rows[0][0],
            "columns": columns,
            "rows": rows,
        },
    }


def test_planted_heat_anomaly_is_one_window() -> None:
    windows = danger_windows(danger_site())
    heat = [window for window in windows if window["variable"] == "tmax_c"]
    assert len(heat) == 1
    window = heat[0]
    assert window["start_date"] == "2010-06-29"
    assert window["end_date"] == "2010-07-05"
    assert window["days"] == 7
    assert window["peak_z"] > 2.0
    assert window["peak_date"].startswith("2010-07")
    assert window["source"] == "computed"


def test_constant_series_never_raises_a_false_alarm() -> None:
    site = danger_site(years=range(2000, 2010))
    for row in site["daily"]["rows"]:
        row[3] = 30.0
        row[4] = 0.0
    assert danger_windows(site) == []


def test_variables_absent_from_the_cache_are_skipped() -> None:
    site = {
        "daily": {
            "source": "nasa:POWER synthetic test fixture",
            "start": "2010-01-01",
            "columns": ["date", "precip_mm"],
            "rows": [
                [(date(2010, 1, 1) + timedelta(days=offset)).isoformat(), 0.0]
                for offset in range(365)
            ],
        }
    }
    assert danger_windows(site) == []


def test_windows_are_sorted_and_have_iso_keys() -> None:
    windows = danger_windows(danger_site())
    assert windows == sorted(windows, key=lambda item: (item["start_date"], item["variable"]))
    for window in windows:
        assert set(window) == {
            "variable",
            "start_date",
            "end_date",
            "days",
            "peak_z",
            "peak_date",
            "source",
        }
        assert window["days"] >= 5
        assert abs(window["peak_z"]) > 2.0
