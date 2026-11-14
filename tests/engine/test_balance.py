# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Hand-checked FAO-56 balance cases plus the documented model simplifications."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from engine.crops import Crop, default_catalogue
from engine.soil import SoilClassError, get_soil_class
from engine.waterbalance import (
    daily_water_balance,
    nrcs_runoff,
    stage_kc,
    window_from_metrics,
)


def synthetic_crop(**overrides: Any) -> Crop:
    parameters: dict[str, Any] = {
        "crop_id": "test_crop",
        "label": "Test crop",
        "family": "cereal",
        "season": "summer",
        "stages_days": {"initial": 1, "development": 0, "mid": 2, "late": 1},
        "kc": {"initial": 1.0, "mid": 1.0, "late": 1.0},
        "root_depth_m": 1.0,
        "depletion_fraction": 0.5,
        "ky": 1.0,
        "n_credit_low": 0.0,
        "n_credit_high": 0.0,
        "n_credit_source": "computed",
        "planting_window": None,
    }
    parameters.update(overrides)
    return Crop(**parameters)


def weather_rows(
    start: str,
    count: int,
    *,
    precip: float = 0.0,
    tmean: float = 20.0,
    tmin: float = 15.0,
    tmax: float = 25.0,
) -> list[dict[str, Any]]:
    first = date.fromisoformat(start)
    return [
        {
            "date": (first + timedelta(days=offset)).isoformat(),
            "tmean_c": tmean,
            "tmin_c": tmin,
            "tmax_c": tmax,
            "precip_mm": precip,
            "rh_pct": 50.0,
            "wind_ms": 2.0,
            "solar_mj_m2": 20.0,
        }
        for offset in range(count)
    ]


def et0_map(start: str, values: list[float]) -> dict[date, float]:
    first = date.fromisoformat(start)
    return {first + timedelta(days=offset): value for offset, value in enumerate(values)}


def test_soil_class_reads_the_config_file() -> None:
    soil = get_soil_class("clay_loam")
    assert soil.theta_fc == pytest.approx(0.36)
    assert soil.theta_wp == pytest.approx(0.20)
    assert soil.available_water_fraction == pytest.approx(0.16)


def test_unknown_soil_class_is_a_clear_error() -> None:
    with pytest.raises(SoilClassError, match="unknown soil class"):
        get_soil_class("moon_dust")


def test_nrcs_runoff_matches_hand_arithmetic() -> None:
    storage = 25400.0 / 75.0 - 254.0
    effective = 30.0 - 0.2 * storage
    expected = effective * effective / (effective + storage)
    assert nrcs_runoff(30.0, 75.0) == pytest.approx(expected)
    assert nrcs_runoff(0.0, 75.0) == 0.0
    assert nrcs_runoff(10.0, 75.0) == 0.0


def test_stage_kc_follows_the_four_stage_curve() -> None:
    crop = synthetic_crop(
        stages_days={"initial": 2, "development": 2, "mid": 2, "late": 2},
        kc={"initial": 0.4, "mid": 1.2, "late": 0.5},
    )
    assert stage_kc(crop, 0) == pytest.approx(0.4)
    assert stage_kc(crop, 2) == pytest.approx(0.4)
    assert stage_kc(crop, 3) == pytest.approx(0.8)
    assert stage_kc(crop, 4) == pytest.approx(1.2)
    assert stage_kc(crop, 6) == pytest.approx(1.2)
    assert stage_kc(crop, 7) == pytest.approx(0.85)
    assert stage_kc(crop, 8) == pytest.approx(0.5)
    assert stage_kc(default_catalogue().get("fallow"), 3) == 0.0


def test_golden_balance_without_stress() -> None:
    metrics = daily_water_balance(
        crop=synthetic_crop(),
        weather_rows=weather_rows("2020-06-01", 4),
        soil_class="clay_loam",
        irrigated=False,
        et0_by_date=et0_map("2020-06-01", [10.0, 10.0, 10.0, 10.0]),
    )
    assert metrics["water_use_mm"] == pytest.approx(40.0)
    assert metrics["irrigation_mm"] == pytest.approx(0.0)
    assert metrics["stress_days"] == 0
    assert metrics["deficit_days"] == 0
    assert metrics["bare_days"] == 0
    assert metrics["max_depletion_mm"] == pytest.approx(40.0)
    assert metrics["erosion_index"] == pytest.approx(0.0)
    assert metrics["n_credit_kg_ha"] == {"low": 0.0, "high": 0.0, "source": "computed"}
    assert metrics["source"] == "computed"
    assert metrics["balance_residual_mm"] == pytest.approx(0.0, abs=1e-6)
    assert metrics["daily_depletion_mm"] == pytest.approx([10.0, 20.0, 30.0, 40.0])


def test_transpiration_is_capped_by_available_water() -> None:
    metrics = daily_water_balance(
        crop=synthetic_crop(),
        weather_rows=weather_rows("2020-06-01", 2),
        soil_class="clay_loam",
        irrigated=False,
        et0_by_date=et0_map("2020-06-01", [100.0, 100.0]),
    )
    assert metrics["max_depletion_mm"] == pytest.approx(160.0)
    assert metrics["stress_days"] == 1
    assert metrics["deficit_days"] == 1
    assert metrics["water_use_mm"] == pytest.approx(160.0)
    assert metrics["balance_residual_mm"] == pytest.approx(0.0, abs=1e-6)
    assert metrics["unmet_et_mm"] == pytest.approx(0.0)


def test_irrigated_site_refills_at_raw_and_reports_gross_depth() -> None:
    metrics = daily_water_balance(
        crop=synthetic_crop(),
        weather_rows=weather_rows("2020-06-01", 9),
        soil_class="clay_loam",
        irrigated=True,
        et0_by_date=et0_map("2020-06-01", [10.0] * 9),
    )
    assert metrics["max_depletion_mm"] == pytest.approx(80.0)
    assert metrics["irrigation_mm"] == pytest.approx(100.0)
    assert metrics["water_use_mm"] == pytest.approx(90.0)
    assert metrics["stress_days"] == 0
    assert metrics["balance_residual_mm"] == pytest.approx(0.0, abs=1e-6)


def test_farmer_irrigation_log_uses_gross_depth_and_efficiency() -> None:
    metrics = daily_water_balance(
        crop=synthetic_crop(),
        weather_rows=weather_rows("2020-06-01", 2),
        soil_class="clay_loam",
        irrigated=True,
        irrigation_log={"2020-06-01": 50.0},
        et0_by_date=et0_map("2020-06-01", [10.0, 10.0]),
    )
    assert metrics["irrigation_mm"] == pytest.approx(50.0)
    assert metrics["water_use_mm"] == pytest.approx(20.0)
    assert metrics["max_depletion_mm"] == pytest.approx(10.0)
    assert metrics["daily_depletion_mm"] == pytest.approx([0.0, 10.0])


def test_fallow_counts_bare_days_and_erosive_rain() -> None:
    fallow = default_catalogue().get("fallow")
    rows = weather_rows("2020-06-01", 3)
    for row, amount in zip(rows, [30.0, 20.0, 40.0], strict=True):
        row["precip_mm"] = amount
    metrics = daily_water_balance(
        crop=fallow,
        weather_rows=rows,
        soil_class="clay_loam",
        irrigated=False,
        et0_by_date=et0_map("2020-06-01", [5.0, 5.0, 5.0]),
    )
    assert metrics["bare_days"] == 3
    assert metrics["water_use_mm"] == pytest.approx(0.0)
    assert metrics["erosion_index"] == pytest.approx(20.0)
    assert metrics["stress_days"] == 0


def test_rotation_schedule_reports_the_maximum_legume_credit() -> None:
    catalogue = default_catalogue()
    berseem = catalogue.get("berseem_clover")
    wheat = catalogue.get("wheat")
    first = date(2020, 10, 20)
    schedule = {
        first: (berseem, 0),
        first + timedelta(days=1): (wheat, 0),
    }
    metrics = daily_water_balance(
        weather_rows=weather_rows("2020-10-20", 2),
        schedule=schedule,
        soil_class="clay_loam",
        irrigated=False,
        et0_by_date=et0_map("2020-10-20", [2.0, 2.0]),
    )
    assert metrics["n_credit_kg_ha"] == {
        "low": 40.0,
        "high": 70.0,
        "source": "assumption:berseem_n_fixation",
    }


def test_missing_temperature_is_an_error_not_an_imputation() -> None:
    rows = weather_rows("2020-06-01", 1)
    rows[0]["tmax_c"] = None
    with pytest.raises(ValueError, match="missing a temperature"):
        daily_water_balance(
            crop=synthetic_crop(),
            weather_rows=rows,
            soil_class="clay_loam",
            irrigated=False,
        )


def test_balance_is_deterministic() -> None:
    arguments = {
        "crop": synthetic_crop(),
        "weather_rows": weather_rows("2020-06-01", 5),
        "soil_class": "clay_loam",
        "irrigated": False,
        "et0_by_date": et0_map("2020-06-01", [4.0] * 5),
    }
    assert daily_water_balance(**arguments) == daily_water_balance(**arguments)


def test_window_from_metrics_projects_only_contract_fields() -> None:
    metrics = daily_water_balance(
        crop=synthetic_crop(),
        weather_rows=weather_rows("2020-06-01", 4),
        soil_class="clay_loam",
        irrigated=False,
        et0_by_date=et0_map("2020-06-01", [10.0] * 4),
    )
    window = window_from_metrics(metrics, start_year=2020)
    assert window["start_year"] == 2020
    assert window["years"] == [2020, 2021, 2022]
    assert "balance_residual_mm" not in window
