# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""FAO-56 daily reference evapotranspiration (ET0).

Inputs are NASA POWER daily weather: mean/min/max air temperature (°C), mean relative humidity
(%), wind speed at 2 m (m/s) and all-sky shortwave radiation (MJ/m²/day). The implementation
follows FAO Irrigation and Drainage Paper 56, chapter 3 (Penman-Monteith) and chapter 4
(Hargreaves fallback).

Output unit: millimetres per day. Every value is ``source: computed``. When humidity, wind or
solar radiation is missing, the Hargreaves fallback is used and the result carries
``assumption:hargreaves_fallback``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from engine.config import assumption_value

GSC = 0.0820
STEFAN_BOLTZMANN = 4.903e-9
ALBEDO = 0.23
FAO56_K = 900.0


@dataclass(frozen=True)
class ET0Result:
    """One day of reference evapotranspiration."""

    et0_mm: float
    method: str
    source: str = "computed"
    fallback_assumption: str | None = None


def saturation_vapour_pressure(temp_c: float) -> float:
    """Saturation vapour pressure in kPa at a temperature in °C (FAO-56 Eq. 11)."""
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def slope_vapour_pressure_curve(temp_c: float) -> float:
    """Slope of the saturation vapour pressure curve in kPa/°C (FAO-56 Eq. 13)."""
    return 4098.0 * saturation_vapour_pressure(temp_c) / ((temp_c + 237.3) ** 2)


def extraterrestrial_radiation(lat_deg: float, day_of_year: int) -> float:
    """Extraterrestrial radiation Ra in MJ/m²/day (FAO-56 Eqs. 21-25)."""
    if not -90.0 <= lat_deg <= 90.0:
        raise ValueError("lat_deg must be within -90..90")
    if not 1 <= day_of_year <= 366:
        raise ValueError("day_of_year must be within 1..366")

    phi = math.radians(lat_deg)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * day_of_year / 365.0)
    declination = 0.409 * math.sin(2.0 * math.pi * day_of_year / 365.0 - 1.39)
    acos_argument = max(-1.0, min(1.0, -math.tan(phi) * math.tan(declination)))
    sunset_angle = math.acos(acos_argument)
    return (
        (24.0 * 60.0 / math.pi)
        * GSC
        * dr
        * (
            sunset_angle * math.sin(phi) * math.sin(declination)
            + math.cos(phi) * math.cos(declination) * math.sin(sunset_angle)
        )
    )


def hargreaves_et0(
    *, tmean_c: float, tmin_c: float, tmax_c: float, lat_deg: float, day_of_year: int
) -> float:
    """Hargreaves-Samani ET0 in mm/day (FAO-56 Eq. 52)."""
    if tmin_c > tmax_c:
        raise ValueError("tmin_c must not exceed tmax_c")
    ra_mm = extraterrestrial_radiation(lat_deg, day_of_year) * 0.408
    return max(0.0, 0.0023 * (tmean_c + 17.8) * math.sqrt(tmax_c - tmin_c) * ra_mm)


def reference_et0(
    *,
    tmean_c: float,
    tmin_c: float,
    tmax_c: float,
    lat_deg: float,
    day_of_year: int,
    rh_pct: float | None,
    wind_ms: float | None,
    solar_mj_m2: float | None,
    elevation_m: float = 0.0,
) -> ET0Result:
    """Compute daily ET0, using Hargreaves when a Penman-Monteith input is missing.

    Args:
        tmean_c/tmin_c/tmax_c: daily temperatures in °C.
        lat_deg: site latitude in decimal degrees.
        day_of_year: 1-366.
        rh_pct: mean relative humidity in percent; ``None`` triggers the fallback.
        wind_ms: wind speed at 2 m in m/s; ``None`` triggers the fallback.
        solar_mj_m2: all-sky shortwave radiation in MJ/m²/day; ``None`` triggers the fallback.
        elevation_m: site elevation in metres above sea level.

    Returns:
        ET0Result with ``et0_mm >= 0`` and the method used.
    """
    if tmin_c > tmax_c:
        raise ValueError("tmin_c must not exceed tmax_c")
    if not -50.0 <= tmean_c <= 70.0:
        raise ValueError("tmean_c outside the accepted -50..70 °C range")

    missing_penman = rh_pct is None or wind_ms is None or solar_mj_m2 is None
    fallback_enabled = bool(assumption_value("hargreaves_fallback"))
    if missing_penman and not fallback_enabled:
        raise ValueError("Penman-Monteith inputs are missing and the Hargreaves fallback is off")
    if missing_penman:
        value = hargreaves_et0(
            tmean_c=tmean_c, tmin_c=tmin_c, tmax_c=tmax_c, lat_deg=lat_deg, day_of_year=day_of_year
        )
        return ET0Result(
            et0_mm=round(value, 4),
            method="hargreaves",
            fallback_assumption="assumption:hargreaves_fallback",
        )

    assert rh_pct is not None and wind_ms is not None and solar_mj_m2 is not None
    if not 0.0 <= rh_pct <= 100.0:
        raise ValueError("rh_pct must be within 0..100")
    if wind_ms < 0.0:
        raise ValueError("wind_ms must be non-negative")
    if solar_mj_m2 < 0.0:
        raise ValueError("solar_mj_m2 must be non-negative")

    pressure_kpa = 101.3 * (((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26)
    psychrometric = 0.000665 * pressure_kpa
    delta = slope_vapour_pressure_curve(tmean_c)

    es = (saturation_vapour_pressure(tmax_c) + saturation_vapour_pressure(tmin_c)) / 2.0
    ea = es * rh_pct / 100.0

    ra = extraterrestrial_radiation(lat_deg, day_of_year)
    clear_sky = (0.75 + 2e-5 * elevation_m) * ra
    if clear_sky <= 0.0:
        ratio = 0.0
    else:
        ratio = max(0.05, min(1.0, solar_mj_m2 / clear_sky))

    tmax_k = tmax_c + 273.16
    tmin_k = tmin_c + 273.16
    net_shortwave = (1.0 - ALBEDO) * solar_mj_m2
    net_longwave = (
        STEFAN_BOLTZMANN
        * ((tmax_k**4 + tmin_k**4) / 2.0)
        * (0.34 - 0.14 * math.sqrt(max(ea, 0.0)))
        * (1.35 * ratio - 0.35)
    )
    net_radiation = net_shortwave - net_longwave

    numerator = 0.408 * delta * net_radiation + psychrometric * (
        FAO56_K / (tmean_c + 273.0)
    ) * wind_ms * (es - ea)
    denominator = delta + psychrometric * (1.0 + 0.34 * wind_ms)
    value = max(0.0, numerator / denominator)
    return ET0Result(et0_mm=round(value, 4), method="fao56_penman_monteith")


def et0_from_power_row(
    row: dict[str, object],
    *,
    lat_deg: float,
    day_of_year: int,
    elevation_m: float = 0.0,
) -> ET0Result:
    """Compute ET0 from a site-cache row keyed by the contract column names."""

    def number(key: str) -> float | None:
        value = row.get(key)
        return float(value) if isinstance(value, (int, float)) else None

    tmean = number("tmean_c")
    tmin = number("tmin_c")
    tmax = number("tmax_c")
    if tmean is None or tmin is None or tmax is None:
        raise ValueError("row is missing tmean_c, tmin_c or tmax_c")
    return reference_et0(
        tmean_c=tmean,
        tmin_c=tmin,
        tmax_c=tmax,
        lat_deg=lat_deg,
        day_of_year=day_of_year,
        rh_pct=number("rh_pct"),
        wind_ms=number("wind_ms"),
        solar_mj_m2=number("solar_mj_m2"),
        elevation_m=elevation_m,
    )
