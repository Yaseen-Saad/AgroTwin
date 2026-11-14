# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Cache-first resolution: snap, live fetch, 3 s timeout and network-failure fallback."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from helpers import iter_dates, power_payload, transport_for

from contracts.validate import FIXTURES_DIR, load_assumption_ids, load_json, validate_document
from ingest.serve import (
    CACHE_TIMEOUT_S,
    MAX_CACHE_SNAP_KM,
    SiteUnavailable,
    cache_summary,
    get_site,
    get_site_by_id,
    load_cached_sites,
    nearest_cached_site,
    resolve_site,
)

ASSUMPTIONS = load_assumption_ids()
START, END = date(2020, 1, 1), date(2020, 1, 3)


def _install_fixture_cache(cache_dir: Path) -> dict:
    document = load_json(FIXTURES_DIR / "site.delta_01.json")
    (cache_dir / "delta_01.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )
    return document


def test_timeout_budget_is_three_seconds() -> None:
    assert CACHE_TIMEOUT_S == 3.0
    assert MAX_CACHE_SNAP_KM > 0


def test_load_and_nearest_cache(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)
    documents = load_cached_sites(cache_dir)
    assert len(documents) == 1
    nearest, distance = nearest_cached_site(31.0409, 31.3785, cache_dir=cache_dir)
    assert nearest is not None
    assert nearest["site_id"] == "delta_01"
    assert distance == pytest.approx(0.0, abs=1e-6)


def test_nearby_pin_snaps_to_cache_without_network(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)

    def forbidden(_url: str) -> dict:
        raise AssertionError("network must not be used when a cache is nearby")

    resolution = resolve_site(
        31.0410, 31.3780, start=START, end=END, transport=forbidden, cache_dir=cache_dir
    )
    assert resolution.cache_hit is True
    assert resolution.fallback_used is False
    assert resolution.document["site_id"] == "delta_01"
    assert resolution.distance_km is not None and resolution.distance_km < 1.0


def test_far_pin_uses_live_power(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)
    transport = transport_for(power_payload(iter_dates(START, END)))
    resolution = resolve_site(
        10.0, 10.0, start=START, end=END, transport=transport, cache_dir=cache_dir
    )
    assert resolution.cache_hit is False
    assert resolution.fallback_used is False
    assert resolution.document["site_id"].startswith("live_")
    assert validate_document("site", resolution.document, ASSUMPTIONS) == []


def test_live_failure_falls_back_to_nearest_cache(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)

    def broken(_url: str) -> dict:
        raise OSError("network unreachable")

    resolution = resolve_site(
        10.0, 10.0, start=START, end=END, transport=broken, cache_dir=cache_dir
    )
    assert resolution.cache_hit is True
    assert resolution.fallback_used is True
    assert resolution.document["site_id"] == "delta_01"
    assert "network unreachable" in resolution.note


def test_no_cache_and_live_failure_raises(cache_dir: Path) -> None:
    def broken(_url: str) -> dict:
        raise OSError("network unreachable")

    with pytest.raises(SiteUnavailable, match="no cache"):
        resolve_site(10.0, 10.0, start=START, end=END, transport=broken, cache_dir=cache_dir)


def test_get_site_returns_a_document(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)
    document = get_site(31.0409, 31.3785, cache_dir=cache_dir)
    assert document["site_id"] == "delta_01"


def test_get_site_by_id_and_summary(cache_dir: Path) -> None:
    _install_fixture_cache(cache_dir)
    document = get_site_by_id("delta_01", cache_dir=cache_dir)
    assert document["site_id"] == "delta_01"
    summary = cache_summary(cache_dir=cache_dir)
    assert summary[0]["site_id"] == "delta_01"
    assert summary[0]["days"] == 14
    with pytest.raises(SiteUnavailable):
        get_site_by_id("missing_01", cache_dir=cache_dir)
