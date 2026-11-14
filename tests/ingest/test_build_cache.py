# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Cache building: contract validity, day counts, null handling and deterministic output."""

from __future__ import annotations

import json
from datetime import date

import pytest
from helpers import iter_dates, power_payload, transport_for

from contracts.validate import load_assumption_ids, validate_document
from ingest.build_cache import (
    DEMO_LOCATIONS,
    build_caches,
    build_site_document,
    default_end,
    last_complete_year,
)

ASSUMPTIONS = load_assumption_ids()


@pytest.fixture(autouse=True)
def _no_earthdata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)


def test_last_complete_year_and_default_end() -> None:
    assert last_complete_year(date(2026, 11, 14)) == 2025
    assert default_end(date(2026, 11, 14)) == date(2025, 12, 31)


def test_demo_locations_match_spec() -> None:
    by_id = {location.site_id: location for location in DEMO_LOCATIONS}
    assert set(by_id) == {"delta_01", "matruh_01", "sevilla_01"}
    assert (by_id["delta_01"].lat, by_id["delta_01"].lon) == (31.0409, 31.3785)
    assert (by_id["matruh_01"].lat, by_id["matruh_01"].lon) == (31.3543, 27.2373)
    assert (by_id["sevilla_01"].lat, by_id["sevilla_01"].lon) == (37.3891, -5.9845)


def test_built_document_validates_against_the_site_contract(demo_location) -> None:
    start, end = date(2020, 1, 1), date(2020, 1, 3)
    transport = transport_for(power_payload(iter_dates(start, end)))
    document = build_site_document(demo_location, start=start, end=end, transport=transport)
    assert validate_document("site", document, ASSUMPTIONS) == []
    assert document["daily"]["start"] == "2020-01-01"
    assert len(document["daily"]["rows"]) == 3
    assert document["monthly_ndvi"] is None
    assert document["monthly_soil_moisture"] is None


def test_cache_rows_never_contain_fill_values(demo_location) -> None:
    start, end = date(2020, 1, 1), date(2020, 1, 3)
    payload = power_payload(iter_dates(start, end), fill_days=[date(2020, 1, 2)])
    document = build_site_document(
        demo_location, start=start, end=end, transport=transport_for(payload)
    )
    rows = document["daily"]["rows"]
    assert rows[1][1:] == [None] * 7
    assert -999.0 not in [value for row in rows for value in row]


def test_build_caches_writes_three_valid_files(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("EARTHDATA_USERNAME", raising=False)
    monkeypatch.delenv("EARTHDATA_PASSWORD", raising=False)
    start, end = date(2020, 1, 1), date(2020, 1, 3)
    transport = transport_for(power_payload(iter_dates(start, end)))
    summaries = build_caches(start=start, end=end, out_dir=tmp_path, transport=transport)

    assert len(summaries) == 3
    assert len(transport.calls) == 3
    for summary in summaries:
        path = tmp_path / f"{summary['site_id']}.json"
        assert path.exists()
        assert summary["days"] == 3
        assert summary["missing_days"] == 0
        assert summary["missing_value_share"] == 0.0
        assert summary["source"] == "nasa:POWER"
        document = json.loads(path.read_text(encoding="utf-8"))
        assert validate_document("site", document, ASSUMPTIONS) == []
        assert path.read_text(encoding="utf-8").endswith("\n")


def test_written_json_is_two_space_indented(tmp_path, demo_location) -> None:
    start, end = date(2020, 1, 1), date(2020, 1, 2)
    transport = transport_for(power_payload(iter_dates(start, end)))
    build_caches(
        site_ids=[demo_location.site_id],
        start=start,
        end=end,
        out_dir=tmp_path,
        transport=transport,
    )
    text = (tmp_path / f"{demo_location.site_id}.json").read_text(encoding="utf-8")
    assert '\n  "site_id":' in text


def test_unknown_site_is_rejected(tmp_path) -> None:
    with pytest.raises(ValueError, match="unknown site"):
        build_caches(site_ids=["nowhere_01"], out_dir=tmp_path)
