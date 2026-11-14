# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Every fixture validates, and each cross-field rule rejects a targeted corruption."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from contracts.validate import (
    FIXTURES,
    FIXTURES_DIR,
    SCHEMA_FILES,
    check_assumption_tags,
    check_result,
    check_rotation,
    check_scout_run,
    check_site,
    load_assumption_ids,
    load_json,
    main,
    validate_fixture,
)

ASSUMPTIONS = load_assumption_ids()
ALL_FIXTURES = [(kind, name) for kind, names in FIXTURES.items() for name in names]


def _fixture(name: str) -> dict[str, Any]:
    return copy.deepcopy(load_json(FIXTURES_DIR / name))


def test_every_schema_is_version_1_0_0() -> None:
    for kind, path in SCHEMA_FILES.items():
        schema = load_json(path)
        assert schema.get("x-schema-version") == "1.0.0", kind


@pytest.mark.parametrize(("kind", "name"), ALL_FIXTURES)
def test_fixture_is_valid(kind: str, name: str) -> None:
    assert validate_fixture(kind, name, ASSUMPTIONS) == []


def test_validate_all_cli_exits_zero() -> None:
    assert main(["--all"]) == 0


def test_site_rejects_negative_precipitation() -> None:
    site = _fixture("site.delta_01.json")
    columns = site["daily"]["columns"]
    row = site["daily"]["rows"][0]
    row[columns.index("precip_mm")] = -2.5
    assert any("negative precipitation" in error for error in check_site(site))


def test_site_rejects_unsorted_temperatures() -> None:
    site = _fixture("site.delta_01.json")
    columns = site["daily"]["columns"]
    row = site["daily"]["rows"][0]
    row[columns.index("tmin_c")], row[columns.index("tmax_c")] = (
        row[columns.index("tmax_c")],
        row[columns.index("tmin_c")],
    )
    assert any("tmin <= tmean <= tmax" in error for error in check_site(site))


def test_scout_run_requires_calibration_for_vwc() -> None:
    run = _fixture("scout_run.simulated.json")
    run["points"][0]["soil_vwc_pct"] = 22.0
    run["points"][0]["soil_calibration_id"] = None
    assert any("without a calibration id" in error for error in check_scout_run(run))


def test_result_rejects_inverted_percentiles() -> None:
    result = _fixture("result.delta_01.json")
    metric = result["rotations"][0]["metrics"]["profit_per_ha"]
    metric["p10"] = metric["p90"] + 1.0
    assert any("p10 <= median <= p90" in error for error in check_result(result, ASSUMPTIONS))


def test_result_rejects_barcode_red_with_profit() -> None:
    result = _fixture("result.delta_01.json")
    stripe = result["rotations"][0]["barcode"][0]
    stripe["class"] = "red"
    stripe["profit_per_ha"] = abs(stripe["profit_per_ha"]) + 100.0
    errors = check_result(result, ASSUMPTIONS)
    assert any("red but profit is not negative" in error for error in errors)


def test_result_rejects_undeclared_assumption() -> None:
    result = _fixture("result.delta_01.json")
    result["assumptions"][0]["id"] = "not_declared"
    result["assumptions"][0]["source"] = "assumption:not_declared"
    errors = check_result(result, ASSUMPTIONS)
    assert any("not declared in assumptions.yaml" in error for error in errors)


def test_unknown_tag_is_rejected_anywhere_in_a_document() -> None:
    document = {"note": "computed", "nested": [{"source": "assumption:imaginary"}]}
    assert check_assumption_tags(document, ASSUMPTIONS) == [
        "unknown assumption tag 'assumption:imaginary' (add it to assumptions.yaml)"
    ]


def test_rotation_rejects_duplicate_slot() -> None:
    rotation = _fixture("rotation.existing.json")
    rotation["slots"].append(copy.deepcopy(rotation["slots"][0]))
    assert any("duplicate slot" in error for error in check_rotation(rotation))
