# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The provisional crop catalogue loads, validates and declares legume assumptions."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from engine.config import load_assumptions
from engine.crops import DEFAULT_CROPS_PATH, CropError, default_catalogue, load_crops

EXPECTED_CROPS = {
    "wheat",
    "maize",
    "sorghum",
    "berseem_clover",
    "faba_bean",
    "sugar_beet",
    "cotton",
    "fallow",
}


@pytest.fixture(scope="module")
def catalogue():
    return load_crops()


def _catalogue_document() -> dict:
    return yaml.safe_load(DEFAULT_CROPS_PATH.read_text(encoding="utf-8"))


def test_catalogue_contains_every_candidate(catalogue) -> None:
    assert set(catalogue.ids) == EXPECTED_CROPS
    assert catalogue.version == "0.1.0"
    assert "provisional" in catalogue.review_status


def test_wheat_stages_sum_to_the_declared_total(catalogue) -> None:
    wheat = catalogue.get("wheat")
    assert wheat.stages_days == {"initial": 25, "development": 60, "mid": 45, "late": 30}
    assert wheat.total_days == 160


def test_fallow_has_no_transpiration(catalogue) -> None:
    fallow = catalogue.get("fallow")
    assert fallow.total_days == 0
    assert set(fallow.kc.values()) == {0.0}
    assert fallow.is_legume is False


def test_legumes_declare_a_declared_assumption(catalogue) -> None:
    ledger = load_assumptions()
    legumes = [crop for crop in catalogue.crops.values() if crop.is_legume]
    assert {crop.crop_id for crop in legumes} == {"berseem_clover", "faba_bean"}
    for crop in legumes:
        assert crop.n_credit_source.startswith("assumption:")
        assert crop.n_credit_source.split(":", 1)[1] in ledger
        assert crop.n_credit_low <= crop.n_credit_high


def test_cereals_have_no_nitrogen_credit(catalogue) -> None:
    for crop_id in ("wheat", "maize", "sorghum", "sugar_beet", "cotton"):
        assert catalogue.get(crop_id).is_legume is False
        assert catalogue.get(crop_id).n_credit_source == "computed"


def test_unknown_crop_raises_a_clear_error(catalogue) -> None:
    with pytest.raises(CropError, match="unknown crop 'rice'"):
        catalogue.get("rice")


def test_catalogue_is_cached_process_wide() -> None:
    assert default_catalogue() is default_catalogue()


def test_invalid_kc_is_rejected(tmp_path: Path) -> None:
    document = _catalogue_document()
    document["crops"]["maize"]["kc"]["mid"] = 3.5
    target = tmp_path / "crops.yaml"
    target.write_text(yaml.safe_dump(document), encoding="utf-8")
    with pytest.raises(CropError, match="kc 'mid'"):
        load_crops(target)


def test_missing_fallow_is_rejected(tmp_path: Path) -> None:
    document = _catalogue_document()
    document["crops"].pop("fallow")
    target = tmp_path / "crops.yaml"
    target.write_text(yaml.safe_dump(document), encoding="utf-8")
    with pytest.raises(CropError, match="fallow"):
        load_crops(target)


def test_legume_without_assumption_source_is_rejected(tmp_path: Path) -> None:
    document = _catalogue_document()
    document["crops"]["faba_bean"].pop("n_credit_source")
    target = tmp_path / "crops.yaml"
    target.write_text(yaml.safe_dump(document), encoding="utf-8")
    with pytest.raises(CropError, match="nitrogen-credit source"):
        load_crops(target)
