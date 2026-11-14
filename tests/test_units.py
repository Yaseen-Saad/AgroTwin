# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Unit conversions at the engine/API boundary."""

from __future__ import annotations

import pytest

from engine.units import (
    FEDDAN_IN_HA,
    M2_PER_FEDDAN,
    egp_per_feddan_to_ha,
    egp_per_ha_to_feddan,
    feddan_to_ha,
    ha_to_feddan,
    mm_to_m3_per_feddan,
    mm_to_m3_per_ha,
)


def test_feddan_definition_matches_the_contract() -> None:
    assert FEDDAN_IN_HA == 0.42
    assert M2_PER_FEDDAN == pytest.approx(4200.0)


def test_hectare_feddan_round_trip() -> None:
    for feddans in (0.0, 1.0, 2.5, 100.0):
        assert ha_to_feddan(feddan_to_ha(feddans)) == pytest.approx(feddans)


def test_one_millimetre_over_one_hectare_is_ten_cubic_metres() -> None:
    assert mm_to_m3_per_ha(1.0) == pytest.approx(10.0)
    assert mm_to_m3_per_ha(25.0) == pytest.approx(250.0)


def test_one_millimetre_over_one_feddan_is_four_point_two_cubic_metres() -> None:
    assert mm_to_m3_per_feddan(1.0) == pytest.approx(4.2)
    assert mm_to_m3_per_feddan(10.0) == pytest.approx(42.0)


def test_egp_conversion_round_trip() -> None:
    assert egp_per_ha_to_feddan(10_000.0) == pytest.approx(4_200.0)
    assert egp_per_feddan_to_ha(4_200.0) == pytest.approx(10_000.0)
    for value in (0.0, 1.0, 33_333.0):
        assert egp_per_feddan_to_ha(egp_per_ha_to_feddan(value)) == pytest.approx(value)
