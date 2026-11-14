# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Verified POWER catalogue, URL building, fill handling and invalid-response guards."""

from __future__ import annotations

from datetime import date

import pytest
from helpers import iter_dates, power_payload, transport_for

from ingest.power import (
    CONTRACT_COLUMNS,
    POWER_PARAMETERS,
    PowerDataError,
    build_power_url,
    fetch_daily,
    parse_power_payload,
)


def test_contract_columns_match_the_frozen_site_schema() -> None:
    assert CONTRACT_COLUMNS == (
        "date",
        "tmean_c",
        "tmin_c",
        "tmax_c",
        "precip_mm",
        "rh_pct",
        "wind_ms",
        "solar_mj_m2",
    )


def test_power_parameter_names_are_the_verified_catalogue() -> None:
    assert POWER_PARAMETERS == {
        "tmean_c": "T2M",
        "tmin_c": "T2M_MIN",
        "tmax_c": "T2M_MAX",
        "precip_mm": "PRECTOTCORR",
        "rh_pct": "RH2M",
        "wind_ms": "WS2M",
        "solar_mj_m2": "ALLSKY_SFC_SW_DWN",
    }


def test_url_carries_every_parameter_and_the_ag_community() -> None:
    url = build_power_url(lat=31.0409, lon=31.3785, start=date(2020, 1, 1), end=date(2020, 1, 2))
    for name in POWER_PARAMETERS.values():
        assert name in url
    assert "community=AG" in url
    assert "format=JSON" in url
    assert "start=20200101" in url
    assert "end=20200102" in url


@pytest.mark.parametrize(("lat", "lon"), [(91.0, 0.0), (-91.0, 0.0), (0.0, 181.0), (0.0, -181.0)])
def test_url_rejects_out_of_range_coordinates(lat: float, lon: float) -> None:
    with pytest.raises(ValueError):
        build_power_url(lat=lat, lon=lon, start=date(2020, 1, 1), end=date(2020, 1, 2))


def test_fetch_daily_returns_one_row_per_day(three_days) -> None:
    start, end = three_days
    transport = transport_for(power_payload(iter_dates(start, end)))
    daily = fetch_daily(lat=31.04, lon=31.38, start=start, end=end, transport=transport)
    assert daily.expected_days == 3
    assert len(daily.rows) == 3
    assert daily.rows[0][0] == "2020-01-01"
    assert daily.rows[-1][0] == "2020-01-03"
    assert all(len(row) == len(CONTRACT_COLUMNS) for row in daily.rows)


def test_fill_values_become_null_and_are_counted(three_days) -> None:
    start, end = three_days
    payload = power_payload(iter_dates(start, end), fill_days=[date(2020, 1, 2)])
    daily = parse_power_payload(payload, start=start, end=end)
    assert daily.rows[1][1:] == [None] * len(POWER_PARAMETERS)
    assert daily.missing_values == len(POWER_PARAMETERS)
    assert daily.missing_days == ("2020-01-02",)
    assert daily.missing_day_share == pytest.approx(1 / 3)
    assert daily.missing_value_share == pytest.approx(1 / 3)


def test_absent_days_are_emitted_as_null_rows_not_imputed(three_days) -> None:
    start, end = three_days
    payload = power_payload(iter_dates(start, end), omit_days=[date(2020, 1, 3)])
    daily = parse_power_payload(payload, start=start, end=end)
    assert len(daily.rows) == 3
    assert daily.rows[2] == ["2020-01-03", None, None, None, None, None, None, None]
    assert daily.missing_days == ("2020-01-03",)


def test_negative_precipitation_is_rejected_not_fixed(three_days) -> None:
    start, end = three_days
    payload = power_payload(iter_dates(start, end), negative_precip_days=[date(2020, 1, 2)])
    with pytest.raises(PowerDataError, match="negative precipitation"):
        parse_power_payload(payload, start=start, end=end)


def test_missing_parameter_block_is_rejected(three_days) -> None:
    start, end = three_days
    payload = power_payload(iter_dates(start, end))
    del payload["properties"]["parameter"]["T2M_MAX"]
    with pytest.raises(PowerDataError, match="T2M_MAX"):
        parse_power_payload(payload, start=start, end=end)


def test_power_messages_are_rejected(three_days) -> None:
    start, end = three_days

    def transport(_url: str) -> dict:
        payload = power_payload(iter_dates(start, end))
        payload["messages"] = ["bad request"]
        return payload

    with pytest.raises(PowerDataError, match="messages"):
        fetch_daily(lat=31.04, lon=31.38, start=start, end=end, transport=transport)


def test_reversed_date_range_is_rejected() -> None:
    payload = power_payload([date(2020, 1, 1)])
    with pytest.raises(ValueError, match="end date"):
        parse_power_payload(payload, start=date(2020, 1, 2), end=date(2020, 1, 1))
