# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Every engine threshold is declared once, tagged and editable."""

from __future__ import annotations

import pytest

from engine.config import AssumptionError, assumption, assumption_value, load_assumptions

REQUIRED_IDS = {
    "heavy_rain_mm",
    "runoff_cn",
    "irrigation_efficiency",
    "amber_margin",
    "sigma_floor",
    "ess_min",
    "post_wetting_hours",
    "confidence_low_below",
    "confidence_high_above",
    "coverage_band_low",
    "coverage_band_high",
    "danger_z",
    "danger_min_days",
    "danger_window_days",
    "tie_band",
    "vision_min_conf",
    "vision_alert_share",
    "vision_alert_min_images",
    "berseem_n_fixation",
    "faba_n_fixation",
    "hargreaves_fallback",
}


def test_every_required_assumption_exists() -> None:
    assert REQUIRED_IDS <= set(load_assumptions())


def test_every_record_is_self_tagged_and_editable() -> None:
    for assumption_id, record in load_assumptions().items():
        assert record["source"] == f"assumption:{assumption_id}", assumption_id
        assert record["editable"] is True, assumption_id
        assert record["unit"], assumption_id
        assert record["description"], assumption_id


def test_numeric_values_are_numbers() -> None:
    for assumption_id, record in load_assumptions().items():
        value = record["value"]
        assert isinstance(value, (int, float, bool)), assumption_id


def test_known_values_match_the_ledger() -> None:
    assert assumption_value("sigma_floor") == 0.05
    assert assumption_value("ess_min") == 5
    assert assumption_value("hargreaves_fallback") is True
    assert assumption_value("danger_z") == 2.0


def test_related_thresholds_are_ordered() -> None:
    assert assumption_value("coverage_band_low") < assumption_value("coverage_band_high")
    assert 1 <= assumption_value("danger_min_days") < assumption_value("danger_window_days") < 366
    assert 0 < assumption_value("amber_margin") < 1


def test_unknown_assumption_raises_a_clear_error() -> None:
    with pytest.raises(AssumptionError, match="unknown assumption 'does_not_exist'"):
        assumption("does_not_exist")


def test_nitrogen_credit_ranges_are_present() -> None:
    berseem = assumption("berseem_n_fixation")
    faba = assumption("faba_n_fixation")
    assert berseem["value"] <= berseem["high"]
    assert faba["value"] <= faba["high"]
    assert berseem["unit"] == faba["unit"] == "kg_N_per_ha"
    for record in (berseem, faba):
        assert "provisional" in record["citation_status"].lower()
