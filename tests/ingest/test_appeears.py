# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""AppEEARS is fail-closed: it never invents satellite values."""

from __future__ import annotations

from datetime import date

from ingest.appeears import (
    NO_CREDENTIALS_NOTE,
    NOT_ENABLED_NOTE,
    credentials_configured,
    fetch_monthly_indices,
)


def test_credentials_require_both_environment_variables() -> None:
    assert credentials_configured({}) is False
    assert credentials_configured({"EARTHDATA_USERNAME": "u"}) is False
    assert credentials_configured({"EARTHDATA_PASSWORD": "p"}) is False
    assert credentials_configured({"EARTHDATA_USERNAME": "u", "EARTHDATA_PASSWORD": "p"}) is True


def test_no_credentials_returns_null_indices_with_a_reason() -> None:
    indices = fetch_monthly_indices(
        lat=31.04, lon=31.38, start=date(2020, 1, 1), end=date(2020, 1, 2), environ={}
    )
    assert indices.monthly_ndvi is None
    assert indices.monthly_soil_moisture is None
    assert indices.available is False
    assert indices.note == NO_CREDENTIALS_NOTE


def test_credentials_without_the_extract_still_return_nulls() -> None:
    indices = fetch_monthly_indices(
        lat=31.04,
        lon=31.38,
        start=date(2020, 1, 1),
        end=date(2020, 1, 2),
        environ={"EARTHDATA_USERNAME": "u", "EARTHDATA_PASSWORD": "p"},
    )
    assert indices.monthly_ndvi is None
    assert indices.monthly_soil_moisture is None
    assert indices.note == NOT_ENABLED_NOTE
