# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Economics, barcode and ranking tests for B-03."""

from __future__ import annotations

import json

import pytest

from agrotwin import REPO_ROOT
from contracts.validate import load_assumption_ids, validate_document
from engine.config import load_assumptions
from engine.econ import (
    EconError,
    barcode,
    economics_for_rotation,
    load_prices,
    profit_per_ha,
    summarize_rotation,
)
from engine.rank import RankError, rank_rotations, sensitivity

WHEAT_ROW = {
    "crop": "wheat",
    "price_egp_per_t": 11000.0,
    "yield_max_t_per_ha": 6.5,
    "variable_cost_egp_per_ha": 25000.0,
    "ky": 1.0,
}


def _window(*, et_a: float = 1000.0, et_c: float = 1000.0, **extra: object) -> dict:
    window = {
        "water_use_mm": et_a,
        "et_c_mm": et_c,
        "irrigation_mm": 100.0,
        "n_credit_kg_ha": {"low": 0.0, "high": 0.0, "source": "computed"},
    }
    window.update(extra)
    return window


def _rotation(
    rotation_id: str,
    *,
    water: float,
    erosion: float,
    credit: float,
    profit: float,
    worst: float,
    loss_share: float = 0.2,
    excluded: bool = False,
    reasons: list[str] | None = None,
) -> dict:
    return {
        "rotation_id": rotation_id,
        "label": rotation_id,
        "metrics": {
            "water_use_mm": {"p10": water, "median": water, "p90": water, "source": "computed"},
            "deficit_days": {"p10": 0, "median": 0, "p90": 0, "source": "computed"},
            "bare_days": {"p10": 0, "median": 0, "p90": 0, "source": "computed"},
            "erosion_index": {
                "p10": erosion,
                "median": erosion,
                "p90": erosion,
                "source": "computed",
            },
            "n_credit_kg_ha": {"low": credit, "high": credit, "source": "computed"},
            "profit_per_ha": {
                "p10": profit,
                "median": profit,
                "p90": profit,
                "currency": "EGP",
                "source": "computed",
            },
            "loss_year_share": {"value": loss_share, "source": "computed"},
        },
        "worst_year": {"year": 1992, "profit_per_ha": worst, "source": "computed"},
        "excluded": {"is_excluded": excluded, "reasons": reasons or []},
    }


def test_prices_cover_every_catalogue_crop() -> None:
    prices = load_prices()
    assert set(prices) == {
        "wheat",
        "maize",
        "sorghum",
        "berseem_clover",
        "faba_bean",
        "sugar_beet",
        "cotton",
        "fallow",
    }


def test_every_price_and_cost_row_has_a_year_and_declared_source() -> None:
    ledger = load_assumptions()
    for crop, row in load_prices().items():
        assert 1981 <= row["year"] <= 2100, crop
        for field in ("price_source", "yield_source", "cost_source"):
            source = row[field]
            assert source.startswith("assumption:"), (crop, field)
            assert source.split(":", 1)[1] in ledger, (crop, field)


def test_economics_for_rotation_expands_planted_slots() -> None:
    rotation = json.loads(
        (REPO_ROOT / "contracts" / "fixtures" / "rotation.existing.json").read_text(
            encoding="utf-8"
        )
    )
    rows = economics_for_rotation(rotation)
    assert len(rows) == 5
    assert [row["crop"] for row in rows].count("wheat") == 3
    assert [row["crop"] for row in rows].count("maize") == 2
    assert all(row["ky"] > 0 for row in rows)


def test_profit_falls_when_price_falls() -> None:
    result = profit_per_ha(
        window_metrics=_window(),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    assert result["low"]["price_mult"] == pytest.approx(0.8)
    assert result["base"]["price_mult"] == pytest.approx(1.0)
    assert result["high"]["price_mult"] == pytest.approx(1.2)
    assert result["low"]["profit_per_ha"] < result["base"]["profit_per_ha"]
    assert result["base"]["profit_per_ha"] < result["high"]["profit_per_ha"]
    assert result["base"]["profit_per_ha"] == pytest.approx(45000.0)
    assert result["source"] == "computed"


def test_yield_loss_lowers_profit() -> None:
    full = profit_per_ha(
        window_metrics=_window(et_a=1000.0, et_c=1000.0),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    stressed = profit_per_ha(
        window_metrics=_window(et_a=800.0, et_c=1000.0),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    assert full["yield_ratio"] == pytest.approx(1.0)
    assert stressed["yield_ratio"] == pytest.approx(0.8)
    assert stressed["base"]["profit_per_ha"] < full["base"]["profit_per_ha"]


def test_legume_credit_always_earns_a_credit() -> None:
    without = profit_per_ha(
        window_metrics=_window(n_credit_kg_ha={"low": 0, "high": 0, "source": "computed"}),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    with_credit = profit_per_ha(
        window_metrics=_window(
            n_credit_kg_ha={
                "low": 40,
                "high": 70,
                "source": "assumption:berseem_n_fixation",
            }
        ),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    assert with_credit["n_credit_value_egp_per_ha"] > 0
    assert with_credit["base"]["profit_per_ha"] > without["base"]["profit_per_ha"]


def test_missing_potential_et_is_rejected() -> None:
    with pytest.raises(EconError, match="et_c_mm"):
        profit_per_ha(
            window_metrics={"water_use_mm": 900.0, "irrigation_mm": 100.0},
            crop_economics=[WHEAT_ROW],
            price_scenario={"price_mult": 1.0},
        )


def test_barcode_classes_worst_year_and_loss_share() -> None:
    result = barcode(
        windows=[
            {"year": 1991, "profit_per_ha": -100.0},
            {"year": 1992, "profit_per_ha": 100.0},
            {"year": 1993, "profit_per_ha": 1000.0},
            {"year": 1994, "profit_per_ha": 5000.0},
        ],
        cost_per_ha=10000.0,
        amber_margin=0.1,
    )
    classes = [stripe["class"] for stripe in result["stripes"]]
    assert classes == ["red", "amber", "green", "green"]
    assert result["worst_year"]["year"] == 1991
    assert result["worst_year"]["profit_per_ha"] == pytest.approx(-100.0)
    assert result["loss_year_share"]["value"] == pytest.approx(0.25)
    assert result["amber_threshold_egp_per_ha"] == pytest.approx(1000.0)
    assert all(stripe["source"] == "computed" for stripe in result["stripes"])


def test_barcode_accepts_a_profit_block() -> None:
    block = profit_per_ha(
        window_metrics=_window(),
        crop_economics=[WHEAT_ROW],
        price_scenario={"price_mult": 1.0},
    )
    result = barcode(
        windows=[{"start_year": 1991, "profit_per_ha": block}],
        cost_per_ha=block["cost_per_ha"],
        amber_margin=0.1,
    )
    assert result["stripes"][0]["year"] == 1991
    assert result["stripes"][0]["profit_per_ha"] == pytest.approx(
        block["base"]["profit_per_ha"]
    )


def test_summarize_rotation_annualises_windows_for_the_result_contract() -> None:
    rotation = json.loads(
        (REPO_ROOT / "contracts" / "fixtures" / "rotation.existing.json").read_text(
            encoding="utf-8"
        )
    )
    windows = [
        {
            "start_year": 2020,
            "water_use_mm": 900.0,
            "deficit_days": 30,
            "bare_days": 60,
            "erosion_index": 3.0,
            "n_credit_kg_ha": {"low": 40, "high": 70, "source": "computed"},
        },
        {
            "start_year": 2021,
            "water_use_mm": 600.0,
            "deficit_days": 0,
            "bare_days": 30,
            "erosion_index": 1.5,
            "n_credit_kg_ha": {"low": 40, "high": 70, "source": "computed"},
        },
    ]
    details = {2020: _window(), 2021: _window(et_a=800.0, et_c=1000.0)}
    summary = summarize_rotation(
        rotation=rotation,
        windows=windows,
        details=details,
        price_scenario={"price_mult": 1.0},
    )
    assert summary["rotation_id"] == "existing"
    assert summary["metrics"]["water_use_mm"]["median"] == pytest.approx(250.0)
    assert summary["metrics"]["deficit_days"]["median"] == pytest.approx(5.0)
    assert summary["metrics"]["bare_days"]["median"] == pytest.approx(15.0)
    assert summary["metrics"]["erosion_index"]["median"] == pytest.approx(0.75)
    expected = profit_per_ha(
        window_metrics=details[2020],
        crop_economics=economics_for_rotation(rotation, prices=load_prices()),
        price_scenario={"price_mult": 1.0},
    )
    assert summary["barcode"][0]["year"] == 2020
    assert summary["barcode"][0]["profit_per_ha"] == pytest.approx(
        expected["base"]["profit_per_ha"] / 3.0
    )
    assert summary["excluded"] == {"is_excluded": False, "reasons": []}


def test_summarized_rotation_fills_a_schema_valid_result_block() -> None:
    rotation = json.loads(
        (REPO_ROOT / "contracts" / "fixtures" / "rotation.existing.json").read_text(
            encoding="utf-8"
        )
    )
    windows = [
        {
            "start_year": 2020,
            "water_use_mm": 900.0,
            "deficit_days": 30,
            "bare_days": 60,
            "erosion_index": 3.0,
            "n_credit_kg_ha": {"low": 40, "high": 70, "source": "computed"},
        },
        {
            "start_year": 2021,
            "water_use_mm": 600.0,
            "deficit_days": 0,
            "bare_days": 30,
            "erosion_index": 1.5,
            "n_credit_kg_ha": {"low": 40, "high": 70, "source": "computed"},
        },
    ]
    details = {2020: _window(), 2021: _window(et_a=800.0, et_c=1000.0)}
    summary = summarize_rotation(
        rotation=rotation,
        windows=windows,
        details=details,
        price_scenario={"price_mult": 1.0},
    )
    template = json.loads(
        (REPO_ROOT / "contracts" / "fixtures" / "result.delta_01.json").read_text(
            encoding="utf-8"
        )
    )
    merged = dict(template["rotations"][0])
    merged.update(summary)
    template["years"] = [2020, 2021]
    template["rotations"] = [merged]
    template["ranking"]["order"] = ["existing"]
    template["ranking"]["weights"] = {"water": 0.34, "soil": 0.33, "profit": 0.33}
    template["ranking"]["tie_band_applied"] = False
    template["fusion"]["weights_by_year"] = {"2020": 0.5, "2021": 0.5}
    assert validate_document("result", template, load_assumption_ids()) == []


def test_water_weight_favours_low_water_and_profit_weight_favours_profit() -> None:
    low_water = _rotation("low_water", water=1000, erosion=5, credit=0, profit=100, worst=50)
    high_profit = _rotation(
        "high_profit", water=2000, erosion=5, credit=0, profit=300, worst=200
    )
    rotations = [low_water, high_profit]
    water_first = rank_rotations(
        rotations=rotations, weights={"water": 1.0, "soil": 0.0, "profit": 0.0}
    )
    profit_first = rank_rotations(
        rotations=rotations, weights={"water": 0.0, "soil": 0.0, "profit": 1.0}
    )
    assert water_first["order"][0] == "low_water"
    assert profit_first["order"][0] == "high_profit"


def test_constraint_excludes_a_rotation_with_a_readable_reason() -> None:
    rotations = [
        _rotation("low_water", water=1000, erosion=5, credit=0, profit=100, worst=50),
        _rotation("high_water", water=2000, erosion=5, credit=0, profit=300, worst=200),
    ]
    result = rank_rotations(
        rotations=rotations,
        weights={"water": 0.34, "soil": 0.33, "profit": 0.33},
        constraints={"max_water_use_mm": 1500},
    )
    assert result["order"] == ["low_water"]
    assert "high_water" not in result["order"]
    assert result["exclusions"]["high_water"]
    assert any("exceeds" in reason for reason in result["exclusions"]["high_water"])


def test_excluded_rotation_never_ranks() -> None:
    rotations = [
        _rotation("blocked", water=1000, erosion=5, credit=0, profit=100, worst=50, excluded=True),
        _rotation("allowed", water=2000, erosion=5, credit=0, profit=300, worst=200),
    ]
    result = rank_rotations(
        rotations=rotations, weights={"water": 0.34, "soil": 0.33, "profit": 0.33}
    )
    assert result["order"] == ["allowed"]
    assert result["exclusions"]["blocked"]


def test_tie_band_reports_no_clear_winner() -> None:
    first = _rotation("first", water=1000, erosion=5, credit=10, profit=100, worst=50)
    second = _rotation("second", water=1000, erosion=5, credit=10, profit=100, worst=50)
    result = rank_rotations(
        rotations=[first, second], weights={"water": 1.0, "soil": 1.0, "profit": 1.0}
    )
    assert result["tie_band_applied"] is True
    assert any("tie_band" in note for note in result["notes"])


def test_weights_are_normalised() -> None:
    result = rank_rotations(
        rotations=[_rotation("one", water=1000, erosion=5, credit=0, profit=100, worst=50)],
        weights={"water": 2.0, "soil": 1.0, "profit": 1.0},
    )
    assert result["weights"] == pytest.approx(
        {"water": 0.5, "soil": 0.25, "profit": 0.25}
    )


def test_all_excluded_returns_an_empty_order() -> None:
    result = rank_rotations(
        rotations=[_rotation("one", water=2000, erosion=5, credit=0, profit=100, worst=50)],
        weights={"water": 1.0, "soil": 0.0, "profit": 0.0},
        constraints={"max_water_use_mm": 500},
    )
    assert result["order"] == []
    assert result["tie_band_applied"] is False


def test_sensitivity_returns_extreme_orders() -> None:
    rotations = [
        _rotation("low_water", water=1000, erosion=5, credit=0, profit=100, worst=50),
        _rotation("high_profit", water=2000, erosion=5, credit=0, profit=300, worst=200),
    ]
    results = sensitivity(
        rotations=rotations,
        extremes=[
            {"water": 1.0, "soil": 0.0, "profit": 0.0},
            {"water": 0.0, "soil": 0.0, "profit": 1.0},
        ],
    )
    assert [entry["order"][0] for entry in results] == ["low_water", "high_profit"]
    assert results[0]["weights"]["water"] == pytest.approx(1.0)


def test_zero_weights_are_rejected() -> None:
    with pytest.raises(RankError, match="positive"):
        rank_rotations(
            rotations=[_rotation("one", water=1000, erosion=5, credit=0, profit=1, worst=1)],
            weights={"water": 0.0, "soil": 0.0, "profit": 0.0},
        )
