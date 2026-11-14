# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Replay windows are deterministic, contract-valid and inside the two-second budget."""

from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from contracts.validate import FIXTURES_DIR, load_assumption_ids, validate_document
from engine.crops import default_catalogue
from engine.replay import (
    ReplayError,
    planting_date,
    rotation_schedule,
    run_replay,
)

ASSUMPTIONS = load_assumption_ids()
CACHE = Path(__file__).resolve().parents[2] / "data" / "cache" / "delta_01.json"
ROTATION_NAMES = ("existing", "alt_water", "alt_soil")


def _rotation(name: str) -> dict[str, Any]:
    path = FIXTURES_DIR / f"rotation.{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def synthetic_site() -> dict[str, Any]:
    start = date(2020, 1, 1)
    end = date(2023, 12, 31)
    rows = []
    for offset in range((end - start).days + 1):
        day = start + timedelta(days=offset)
        rows.append(
            [day.isoformat(), 25.0, 20.0, 30.0, 0.0, 50.0, 2.0, 20.0]
        )
    return {
        "site_id": "test_site",
        "name": "Synthetic four-year site",
        "lat": 31.0,
        "lon": 31.0,
        "elevation_m": 10,
        "irrigation": "rainfed",
        "soil_class": "clay_loam",
        "timezone": "UTC",
        "generated_by": "test",
        "daily": {
            "source": "nasa:POWER synthetic test fixture",
            "start": start.isoformat(),
            "columns": [
                "date",
                "tmean_c",
                "tmin_c",
                "tmax_c",
                "precip_mm",
                "rh_pct",
                "wind_ms",
                "solar_mj_m2",
            ],
            "rows": rows,
        },
    }


def test_planting_date_is_the_window_midpoint() -> None:
    catalogue = default_catalogue()
    assert planting_date(catalogue.get("wheat"), 2020) == date(2020, 11, 7)
    assert planting_date(catalogue.get("maize"), 2020) == date(2020, 5, 15)


def test_rotation_schedule_stays_inside_the_window() -> None:
    catalogue = default_catalogue()
    window_start = date(2020, 1, 1)
    window_end = date(2022, 12, 31)
    schedule = rotation_schedule(
        _rotation("existing"),
        catalogue,
        start_year=2020,
        window_start=window_start,
        window_end=window_end,
    )
    assert schedule
    assert min(schedule) >= window_start
    assert max(schedule) <= window_end
    assert all(isinstance(entry[1], int) for entry in schedule.values())


def test_replay_is_contract_valid_and_deterministic() -> None:
    site = synthetic_site()
    rotations = [_rotation("existing")]
    scenario = {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0}

    document = run_replay(site, rotations, scenario)
    assert validate_document("replay", document, ASSUMPTIONS) == []
    assert document["years"] == [2020, 2021]
    assert document["mode"] == "NONE"
    assert len(document["rotations"]) == 1
    windows = document["rotations"][0]["windows"]
    assert len(windows) == 2
    assert windows[0]["years"] == [2020, 2021, 2022]
    assert windows[1]["years"] == [2021, 2022, 2023]
    assert all(window["source"] == "computed" for window in windows)
    assert run_replay(site, rotations, scenario) == document


def test_replay_details_expose_potential_et_for_economics() -> None:
    site = synthetic_site()
    scenario = {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0}
    document, details = run_replay(
        site, [_rotation("existing")], scenario, with_details=True
    )
    assert validate_document("replay", document, ASSUMPTIONS) == []
    first = details["existing"][2020]
    assert first["et_c_mm"] >= first["water_use_mm"]
    assert first["n_credit_kg_ha"]["source"].startswith(("assumption:", "computed"))
    assert first["stress_days"] >= first["deficit_days"] >= 0


def test_replay_accepts_every_mode() -> None:
    site = synthetic_site()
    rotations = [_rotation("existing")]
    scenario = {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0}
    for mode in ("LIVE", "REPLAY", "SIMULATED", "NONE"):
        assert run_replay(site, rotations, scenario, mode=mode)["mode"] == mode


def test_replay_rejects_an_unknown_mode() -> None:
    with pytest.raises(ReplayError, match="mode"):
        run_replay(
            synthetic_site(),
            [_rotation("existing")],
            {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0},
            mode="PREDICTED",
        )


def test_replay_rejects_a_cache_shorter_than_three_years() -> None:
    site = synthetic_site()
    site["daily"]["rows"] = site["daily"]["rows"][: 365 * 2]
    with pytest.raises(ReplayError, match="three calendar years"):
        run_replay(
            site,
            [_rotation("existing")],
            {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0},
        )


@pytest.mark.parametrize(
    "scenario",
    [
        {"rain_mult": -0.1, "temp_offset_c": 0.0, "price_mult": 1.0},
        {"rain_mult": 1.0, "temp_offset_c": 11.0, "price_mult": 1.0},
        {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 6.0},
        {"rain_mult": 1.0, "temp_offset_c": 0.0},
    ],
)
def test_replay_rejects_out_of_contract_scenarios(scenario: dict[str, float]) -> None:
    with pytest.raises(ReplayError):
        run_replay(synthetic_site(), [_rotation("existing")], scenario)


@pytest.mark.skipif(not CACHE.exists(), reason="no generated cache; run ingest.build_cache")
def test_real_cache_replay_is_valid_and_fast() -> None:
    site = json.loads(CACHE.read_text(encoding="utf-8"))
    rotations = [_rotation(name) for name in ROTATION_NAMES]
    scenario = {"rain_mult": 1.0, "temp_offset_c": 0.0, "price_mult": 1.0}

    started = time.perf_counter()
    document = run_replay(site, rotations, scenario)
    elapsed = time.perf_counter() - started

    assert validate_document("replay", document, ASSUMPTIONS) == []
    assert elapsed < 2.0
    assert len(document["years"]) == 33
    assert [len(block["windows"]) for block in document["rotations"]] == [33, 33, 33]
