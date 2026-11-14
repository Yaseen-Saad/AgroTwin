# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Daily single-crop and rotation soil water balance (FAO-56 root-zone depletion method).

Model (FAO Irrigation and Drainage Paper 56, chapters 8 and 9)::

    TAW   = 1000 * (theta_FC - theta_WP) * Z_r          [mm]
    RAW   = p * TAW                                      [mm]
    K_s   = 1                              when D_r <= RAW
    K_s   = (TAW - D_r) / ((1 - p) * TAW)  when D_r > RAW
    ET_c  = K_c * ET_0
    ET_a  = K_s * ET_c
    D_r,i = D_r,i-1 - (P_i - RO_i) - I_i - CR_i + ET_a,i + DP_i

Implementation choices, all deliberately visible:

- ``K_c`` follows the four-stage curve in ``engine/crops.yaml`` (initial / development / mid /
  late); stage lengths are days, not fractions.
- Runoff uses the NRCS curve number ``assumption:runoff_cn`` (S = 25400/CN - 254, Ia = 0.2 S).
- Capillary rise ``CR`` is not modelled and is zero.
- On an irrigated site with no farmer log, the root zone refills to field capacity whenever
  depletion reaches RAW. Gross applied water is net / ``assumption:irrigation_efficiency``.
- A farmer-supplied ``irrigation_log`` (ISO date -> gross mm) overrides automatic refill.
- Fallow and any day without an active crop have ``K_c = 0`` and count as bare. Bare days carry
  no root-zone storage in this model, so rain on a bare day becomes deep percolation; erosion
  exposure sums ``max(0, P - assumption:heavy_rain_mm)`` on those days.
- If a day's demand would push depletion past TAW, actual transpiration is reduced to the water
  that is physically available, so ``D_r`` never exceeds TAW and the balance closes.
- ``water_use_mm`` is actual crop transpiration (``ET_a``); bare-soil evaporation is not
  modelled. ``stress_days`` counts crop days with ``K_s < 1``; ``deficit_days`` counts crop days
  that end at or below wilting point (a severe deficit, a subset of stress days).
- A change of root depth (a new crop) clamps the depletion to the new TAW. The storage jump is a
  model reset, not a water flux, so it is excluded from the balance residual.
- Missing humidity, wind or solar radiation falls back to Hargreaves inside ``engine.et0`` and
  is tagged there. Missing temperatures are an error, never imputed.

Outputs are ``computed``; no value is a forecast.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from engine.config import assumption_value
from engine.crops import Crop
from engine.et0 import reference_et0
from engine.soil import get_soil_class

SOURCE_TAG = "computed"
EPSILON = 1e-9
DATE_KEY = "date"


def _number(row: Mapping[str, Any], key: str) -> float | None:
    value = row.get(key)
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _row_date(row: Mapping[str, Any]) -> date:
    raw = row.get(DATE_KEY)
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        return date.fromisoformat(raw)
    raise ValueError(f"weather row is missing an ISO date: {raw!r}")


def nrcs_runoff(precip_mm: float, curve_number: float) -> float:
    """NRCS curve-number runoff in mm for one day of rainfall."""
    if precip_mm <= 0.0:
        return 0.0
    if not 1.0 <= curve_number <= 100.0:
        raise ValueError("curve_number must be within 1..100")
    storage = 25400.0 / curve_number - 254.0
    initial_abstraction = 0.2 * storage
    if precip_mm <= initial_abstraction:
        return 0.0
    effective = precip_mm - initial_abstraction
    return (effective * effective) / (effective + storage)


def stage_kc(crop: Crop, day_index: int) -> float:
    """Crop coefficient for a 0-based day since planting (FAO-56 K_c curve)."""
    if crop.crop_id == "fallow" or day_index < 0:
        return 0.0
    initial, development, mid, late = (
        crop.stages_days["initial"],
        crop.stages_days["development"],
        crop.stages_days["mid"],
        crop.stages_days["late"],
    )
    total = initial + development + mid + late
    if total <= 0:
        return 0.0
    if day_index < initial:
        return crop.kc["initial"]
    if day_index < initial + development:
        fraction = (day_index - initial) / development if development else 1.0
        return crop.kc["initial"] + fraction * (crop.kc["mid"] - crop.kc["initial"])
    if day_index < initial + development + mid:
        return crop.kc["mid"]
    if day_index < total:
        fraction = (day_index - initial - development - mid) / late if late else 1.0
        return crop.kc["mid"] + fraction * (crop.kc["late"] - crop.kc["mid"])
    return crop.kc["late"]


@dataclass(frozen=True)
class PreparedWeather:
    """Typed daily weather columns, sorted by date and already scenario-adjusted.

    Built once for a site cache and sliced per replay window so the hot loop never touches
    dictionaries or ISO strings.
    """

    days: list[date]
    tmean_c: list[float]
    tmin_c: list[float]
    tmax_c: list[float]
    rain_mm: list[float]
    runoff_mm: list[float]
    rh_pct: list[float | None]
    wind_ms: list[float | None]
    solar_mj_m2: list[float | None]

    def __len__(self) -> int:
        return len(self.days)

    def slice(self, start: int, stop: int) -> PreparedWeather:
        """Return a window view with every column sliced in step."""
        return PreparedWeather(
            days=self.days[start:stop],
            tmean_c=self.tmean_c[start:stop],
            tmin_c=self.tmin_c[start:stop],
            tmax_c=self.tmax_c[start:stop],
            rain_mm=self.rain_mm[start:stop],
            runoff_mm=self.runoff_mm[start:stop],
            rh_pct=self.rh_pct[start:stop],
            wind_ms=self.wind_ms[start:stop],
            solar_mj_m2=self.solar_mj_m2[start:stop],
        )


def prepare_weather(
    weather_rows: Sequence[Mapping[str, Any]],
    *,
    rain_mult: float = 1.0,
    temp_offset_c: float = 0.0,
) -> PreparedWeather:
    """Sort and type the frozen site rows, applying the scenario transforms once."""
    if rain_mult < 0.0:
        raise ValueError("rain_mult must not be negative")
    pairs = sorted(
        ((_row_date(row), row) for row in weather_rows),
        key=lambda pair: pair[0],
    )
    if not pairs:
        raise ValueError("weather_rows must not be empty")

    curve_number = float(assumption_value("runoff_cn"))
    prepared = PreparedWeather([], [], [], [], [], [], [], [], [])
    for day, row in pairs:
        tmean = _number(row, "tmean_c")
        tmin = _number(row, "tmin_c")
        tmax = _number(row, "tmax_c")
        if tmean is None or tmin is None or tmax is None:
            raise ValueError(f"weather row {day.isoformat()} is missing a temperature")
        raw_rain = _number(row, "precip_mm")
        rain = max(0.0, (0.0 if raw_rain is None else raw_rain) * rain_mult)
        prepared.days.append(day)
        prepared.tmean_c.append(tmean + temp_offset_c)
        prepared.tmin_c.append(tmin + temp_offset_c)
        prepared.tmax_c.append(tmax + temp_offset_c)
        prepared.rain_mm.append(rain)
        prepared.runoff_mm.append(nrcs_runoff(rain, curve_number))
        prepared.rh_pct.append(_number(row, "rh_pct"))
        prepared.wind_ms.append(_number(row, "wind_ms"))
        prepared.solar_mj_m2.append(_number(row, "solar_mj_m2"))
    return prepared


def _normalise_schedule(
    schedule: Mapping[date, tuple[Crop, int]],
) -> dict[date, tuple[Crop, int]]:
    normalised: dict[date, tuple[Crop, int]] = {}
    for day, entry in schedule.items():
        key = day if isinstance(day, date) else date.fromisoformat(str(day))
        normalised[key] = entry
    return normalised


def _single_crop_schedule(crop: Crop, days: Sequence[date]) -> dict[date, tuple[Crop, int]]:
    if crop.crop_id == "fallow":
        return {}
    return {day: (crop, index) for index, day in enumerate(days)}


def _credit_for_schedule(
    schedule: Mapping[date, tuple[Crop, int]],
) -> dict[str, Any]:
    """Return the rotation-level nitrogen credit (maximum legume credit, not a sum)."""
    best: Crop | None = None
    for crop, _index in schedule.values():
        if crop.n_credit_high <= 0:
            continue
        if best is None or crop.n_credit_high > best.n_credit_high:
            best = crop
    if best is None:
        return {"low": 0.0, "high": 0.0, "source": SOURCE_TAG}
    return {
        "low": float(best.n_credit_low),
        "high": float(best.n_credit_high),
        "source": best.n_credit_source,
    }


def et0_series(
    prepared: PreparedWeather,
    *,
    lat_deg: float,
    elevation_m: float = 0.0,
) -> list[float]:
    """Compute ET0 for every prepared day with the site coordinates."""
    return [
        reference_et0(
            tmean_c=prepared.tmean_c[index],
            tmin_c=prepared.tmin_c[index],
            tmax_c=prepared.tmax_c[index],
            lat_deg=lat_deg,
            day_of_year=prepared.days[index].timetuple().tm_yday,
            rh_pct=prepared.rh_pct[index],
            wind_ms=prepared.wind_ms[index],
            solar_mj_m2=prepared.solar_mj_m2[index],
            elevation_m=elevation_m,
        ).et0_mm
        for index in range(len(prepared))
    ]


def _et0_values(
    prepared: PreparedWeather,
    *,
    lat_deg: float,
    elevation_m: float,
    et0_by_date: Mapping[date | str, float] | None,
) -> list[float]:
    lookup: dict[date, float] = {}
    if et0_by_date is not None:
        for key, value in et0_by_date.items():
            day = key if isinstance(key, date) else date.fromisoformat(str(key))
            lookup[day] = float(value)

    values: list[float] = []
    for index, day in enumerate(prepared.days):
        cached = lookup.get(day)
        if cached is not None:
            values.append(cached)
            continue
        values.append(
            reference_et0(
                tmean_c=prepared.tmean_c[index],
                tmin_c=prepared.tmin_c[index],
                tmax_c=prepared.tmax_c[index],
                lat_deg=lat_deg,
                day_of_year=day.timetuple().tm_yday,
                rh_pct=prepared.rh_pct[index],
                wind_ms=prepared.wind_ms[index],
                solar_mj_m2=prepared.solar_mj_m2[index],
                elevation_m=elevation_m,
            ).et0_mm
        )
    return values


def balance_metrics(
    prepared: PreparedWeather,
    schedule: Mapping[date, tuple[Crop, int]],
    *,
    et0_values: Sequence[float],
    soil_awc: float,
    irrigated: bool,
    irrigation_efficiency: float,
    heavy_rain_mm: float,
    irrigation_log: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Run the hot daily loop over prepared columns and return the window metrics."""
    if len(et0_values) != len(prepared):
        raise ValueError("et0_values must align with prepared weather rows")

    log: dict[date, float] = {}
    for key, value in (irrigation_log or {}).items():
        day = key if isinstance(key, date) else date.fromisoformat(str(key))
        depth = float(value)
        if depth < 0.0:
            raise ValueError(f"negative irrigation depth on {day.isoformat()}")
        log[day] = depth

    kc_by_day = {
        day: stage_kc(scheduled_crop, day_index)
        for day, (scheduled_crop, day_index) in schedule.items()
    }

    depletion = 0.0
    previous_taw = 0.0
    water_use = 0.0
    potential_et = 0.0
    irrigation_gross = 0.0
    stress_days = 0
    deficit_days = 0
    bare_days = 0
    erosion_index = 0.0
    max_depletion = 0.0
    residual = 0.0
    unmet_et = 0.0
    daily_depletion: list[float] = []
    taw_cache: dict[str, tuple[float, float]] = {}

    for index, day in enumerate(prepared.days):
        entry = schedule.get(day)
        if entry is None or entry[0].crop_id == "fallow":
            is_bare = True
            taw = 0.0
            ratio_threshold = 0.0
        else:
            is_bare = False
            active_crop = entry[0]
            cached_taw = taw_cache.get(active_crop.crop_id)
            if cached_taw is None:
                taw = 1000.0 * soil_awc * active_crop.root_depth_m
                ratio_threshold = active_crop.depletion_fraction
                taw_cache[active_crop.crop_id] = (taw, ratio_threshold)
            else:
                taw, ratio_threshold = cached_taw

        if taw != previous_taw:
            depletion = min(max(depletion, 0.0), taw) if taw > 0.0 else 0.0
            previous_taw = taw

        raw = ratio_threshold * taw
        precip = prepared.rain_mm[index]
        runoff = prepared.runoff_mm[index]

        irrigation_net = 0.0
        gross = log.get(day)
        if gross is not None:
            irrigation_net = gross * irrigation_efficiency
            irrigation_gross += gross
        elif irrigated and taw > 0.0 and depletion >= raw - EPSILON:
            irrigation_net = depletion
            irrigation_gross += depletion / irrigation_efficiency
            depletion = 0.0

        if taw <= 0.0:
            ks = 0.0
        elif depletion <= raw + EPSILON:
            ks = 1.0
        elif ratio_threshold < 1.0:
            ks = (taw - depletion) / ((1.0 - ratio_threshold) * taw)
            ks = 0.0 if ks < 0.0 else (1.0 if ks > 1.0 else ks)
        else:
            ks = 0.0

        et_c_day = 0.0 if is_bare else kc_by_day.get(day, 0.0) * et0_values[index]
        eta = ks * et_c_day
        potential_et += et_c_day

        storage_before = taw - depletion
        depletion = depletion - (precip - runoff) - irrigation_net + eta
        deep_percolation = 0.0
        if depletion < 0.0:
            deep_percolation = -depletion
            depletion = 0.0
        elif taw > 0.0 and depletion > taw:
            overshoot = depletion - taw
            reduction = eta if eta < overshoot else overshoot
            eta -= reduction
            unmet_et += overshoot - reduction
            depletion = taw
        elif taw <= 0.0:
            depletion = 0.0
        storage_after = taw - depletion
        residual += (precip - runoff) + irrigation_net - eta - deep_percolation
        residual -= storage_after - storage_before

        water_use += eta
        if not is_bare and ks < 1.0 - EPSILON:
            stress_days += 1
        if not is_bare and depletion >= taw - EPSILON:
            deficit_days += 1
        if is_bare:
            bare_days += 1
            if precip > heavy_rain_mm:
                erosion_index += precip - heavy_rain_mm
        if depletion > max_depletion:
            max_depletion = depletion
        daily_depletion.append(depletion)

    return {
        "water_use_mm": round(water_use, 3),
        "et_c_mm": round(potential_et, 3),
        "irrigation_mm": round(irrigation_gross, 3),
        "deficit_days": deficit_days,
        "stress_days": stress_days,
        "bare_days": bare_days,
        "erosion_index": round(erosion_index, 3),
        "max_depletion_mm": round(max_depletion, 3),
        "n_credit_kg_ha": _credit_for_schedule(schedule),
        "source": SOURCE_TAG,
        "balance_residual_mm": round(residual, 6),
        "unmet_et_mm": round(unmet_et, 6),
        "daily_depletion_mm": [round(value, 6) for value in daily_depletion],
    }


def daily_water_balance(
    *,
    crop: Crop | None = None,
    weather_rows: Sequence[Mapping[str, Any]],
    soil_class: str,
    irrigated: bool,
    irrigation_log: Mapping[str, float] | None = None,
    rain_mult: float = 1.0,
    temp_offset_c: float = 0.0,
    lat_deg: float = 0.0,
    elevation_m: float = 0.0,
    et0_by_date: Mapping[date | str, float] | None = None,
    schedule: Mapping[date, tuple[Crop, int]] | None = None,
) -> dict[str, Any]:
    """Run the daily root-zone balance over one window and return agronomic metrics.

    Args:
        crop: The crop that occupies every supplied row when ``schedule`` is omitted. When
            ``schedule`` is supplied, ``crop`` is ignored and may be ``None``.
        weather_rows: Mappings with the frozen site columns (``date``, ``tmean_c``, ...).
        soil_class: A name from ``engine/config/soil_classes.yaml``.
        irrigated: True for an irrigated site (automatic refill at RAW unless a log is given).
        irrigation_log: Optional ISO date -> gross millimetres supplied by the farmer.
        rain_mult: Scenario rainfall multiplier (0..3).
        temp_offset_c: Scenario temperature offset in °C.
        lat_deg/elevation_m: Site coordinates used only when ET0 is computed locally.
        et0_by_date: Optional precomputed ET0 in mm/day, keyed by date or ISO string.
        schedule: Optional date -> ``(crop, day_index_since_planting)`` map for a rotation.

    Returns:
        A mapping with the ``replay.schema.json`` window fields plus diagnostics:
        ``balance_residual_mm``, ``unmet_et_mm`` and ``daily_depletion_mm``.
    """
    soil_awc = get_soil_class(soil_class).available_water_fraction
    irrigation_efficiency = float(assumption_value("irrigation_efficiency"))
    if not 0.0 < irrigation_efficiency <= 1.0:
        raise ValueError("assumption:irrigation_efficiency must be within (0, 1]")

    prepared = prepare_weather(
        weather_rows, rain_mult=rain_mult, temp_offset_c=temp_offset_c
    )
    if schedule is None:
        if crop is None:
            raise ValueError("provide either crop or schedule")
        schedule = _single_crop_schedule(crop, prepared.days)
    normalised = _normalise_schedule(schedule)
    return balance_metrics(
        prepared,
        normalised,
        et0_values=_et0_values(
            prepared,
            lat_deg=lat_deg,
            elevation_m=elevation_m,
            et0_by_date=et0_by_date,
        ),
        soil_awc=soil_awc,
        irrigated=irrigated,
        irrigation_efficiency=irrigation_efficiency,
        heavy_rain_mm=float(assumption_value("heavy_rain_mm")),
        irrigation_log=irrigation_log,
    )


def window_from_metrics(metrics: Mapping[str, Any], *, start_year: int) -> dict[str, Any]:
    """Project balance metrics onto the frozen replay window fields."""
    return {
        "start_year": start_year,
        "years": [start_year, start_year + 1, start_year + 2],
        "water_use_mm": metrics["water_use_mm"],
        "irrigation_mm": metrics["irrigation_mm"],
        "deficit_days": metrics["deficit_days"],
        "stress_days": metrics["stress_days"],
        "bare_days": metrics["bare_days"],
        "erosion_index": metrics["erosion_index"],
        "max_depletion_mm": metrics["max_depletion_mm"],
        "n_credit_kg_ha": metrics["n_credit_kg_ha"],
        "source": metrics["source"],
    }
