# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""FAO-56 ET0 behaviour and the documented Hargreaves fallback."""

from __future__ import annotations

import math

import pytest

from engine.et0 import (
    ET0Result,
    et0_from_power_row,
    extraterrestrial_radiation,
    hargreaves_et0,
    reference_et0,
    saturation_vapour_pressure,
    slope_vapour_pressure_curve,
)


def test_saturation_vapour_pressure_at_zero() -> None:
    assert saturation_vapour_pressure(0.0) == pytest.approx(0.6108, rel=1e-6)


def test_slope_of_vapour_pressure_curve_is_positive() -> None:
    assert slope_vapour_pressure_curve(25.0) > 0.0


def test_extraterrestrial_radiation_summer_mid_latitude() -> None:
    ra = extraterrestrial_radiation(31.0409, 180)
    assert 38.0 < ra < 44.0


def test_extraterrestrial_radiation_polar_night_is_zero() -> None:
    assert extraterrestrial_radiation(80.0, 1) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("lat", [-91.0, 91.0])
def test_extraterrestrial_radiation_rejects_bad_latitude(lat: float) -> None:
    with pytest.raises(ValueError, match="lat_deg"):
        extraterrestrial_radiation(lat, 180)


@pytest.mark.parametrize("doy", [0, 367])
def test_extraterrestrial_radiation_rejects_bad_day(doy: int) -> None:
    with pytest.raises(ValueError, match="day_of_year"):
        extraterrestrial_radiation(31.0, doy)


def test_hargreaves_matches_the_published_formula() -> None:
    ra_mm = extraterrestrial_radiation(31.0409, 180) * 0.408
    expected = 0.0023 * (30.0 + 17.8) * math.sqrt(38.0 - 22.0) * ra_mm
    assert hargreaves_et0(
        tmean_c=30.0, tmin_c=22.0, tmax_c=38.0, lat_deg=31.0409, day_of_year=180
    ) == pytest.approx(expected)


def test_penman_monteith_produces_a_plausible_summer_value() -> None:
    result = reference_et0(
        tmean_c=30.0,
        tmin_c=22.0,
        tmax_c=38.0,
        lat_deg=31.0409,
        day_of_year=180,
        rh_pct=50.0,
        wind_ms=2.0,
        solar_mj_m2=28.0,
        elevation_m=8.0,
    )
    assert isinstance(result, ET0Result)
    assert result.method == "fao56_penman_monteith"
    assert result.source == "computed"
    assert result.fallback_assumption is None
    assert 5.0 < result.et0_mm < 11.0


def test_missing_humidity_uses_hargreaves_and_declares_the_assumption() -> None:
    result = reference_et0(
        tmean_c=30.0,
        tmin_c=22.0,
        tmax_c=38.0,
        lat_deg=31.0409,
        day_of_year=180,
        rh_pct=None,
        wind_ms=2.0,
        solar_mj_m2=28.0,
    )
    assert result.method == "hargreaves"
    assert result.fallback_assumption == "assumption:hargreaves_fallback"
    assert 3.0 < result.et0_mm < 12.0


def test_fallback_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("engine.et0.assumption_value", lambda _: False)
    with pytest.raises(ValueError, match="fallback is off"):
        reference_et0(
            tmean_c=30.0,
            tmin_c=22.0,
            tmax_c=38.0,
            lat_deg=31.0,
            day_of_year=180,
            rh_pct=None,
            wind_ms=2.0,
            solar_mj_m2=28.0,
        )


def test_tmin_above_tmax_is_rejected() -> None:
    with pytest.raises(ValueError, match="tmin_c"):
        reference_et0(
            tmean_c=30.0,
            tmin_c=40.0,
            tmax_c=35.0,
            lat_deg=31.0,
            day_of_year=180,
            rh_pct=50.0,
            wind_ms=2.0,
            solar_mj_m2=28.0,
        )


@pytest.mark.parametrize("rh", [-1.0, 101.0])
def test_relative_humidity_is_range_checked(rh: float) -> None:
    with pytest.raises(ValueError, match="rh_pct"):
        reference_et0(
            tmean_c=30.0,
            tmin_c=22.0,
            tmax_c=38.0,
            lat_deg=31.0,
            day_of_year=180,
            rh_pct=rh,
            wind_ms=2.0,
            solar_mj_m2=28.0,
        )


def test_power_row_adapter_uses_contract_column_names() -> None:
    row = {
        "tmean_c": 30.0,
        "tmin_c": 22.0,
        "tmax_c": 38.0,
        "rh_pct": 50.0,
        "wind_ms": 2.0,
        "solar_mj_m2": 28.0,
    }
    result = et0_from_power_row(row, lat_deg=31.0409, day_of_year=180, elevation_m=8.0)
    assert result.method == "fao56_penman_monteith"
    assert result.et0_mm > 0.0


def test_power_row_adapter_requires_temperatures() -> None:
    with pytest.raises(ValueError, match="tmean_c"):
        et0_from_power_row({"tmax_c": 38.0}, lat_deg=31.0, day_of_year=180)
