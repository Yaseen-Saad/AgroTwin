# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Deterministic POWER payload helpers for ingest tests (no network)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from typing import Any

from ingest.power import POWER_PARAMETERS


def iter_dates(start: date, end: date) -> list[date]:
    """Return every calendar date in the inclusive range."""
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def power_payload(
    days: Iterable[date],
    *,
    fill_days: Iterable[date] = (),
    omit_days: Iterable[date] = (),
    negative_precip_days: Iterable[date] = (),
) -> dict[str, Any]:
    """Build a POWER-shaped payload with deterministic, physically plausible values."""
    fill = {day.isoformat() for day in fill_days}
    omit = {day.isoformat() for day in omit_days}
    negative = {day.isoformat() for day in negative_precip_days}

    series: dict[str, dict[str, float]] = {name: {} for name in POWER_PARAMETERS.values()}
    for index, day in enumerate(days):
        stamp = day.strftime("%Y%m%d")
        if day.isoformat() in omit:
            continue
        if day.isoformat() in fill:
            for name in series:
                series[name][stamp] = -999.0
            continue
        mean = 18.0 + (index % 10) * 0.5
        series["T2M"][stamp] = mean
        series["T2M_MIN"][stamp] = mean - 7.0
        series["T2M_MAX"][stamp] = mean + 7.0
        series["PRECTOTCORR"][stamp] = -1.0 if day.isoformat() in negative else index % 3 * 0.4
        series["RH2M"][stamp] = 55.0
        series["WS2M"][stamp] = 2.5
        series["ALLSKY_SFC_SW_DWN"][stamp] = 20.0

    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [31.3785, 31.0409, 8.0]},
        "properties": {"parameter": series},
        "header": {
            "title": "NASA/POWER Source Native Resolution Daily Data",
            "api": {"version": "test", "name": "POWER Daily API"},
            "sources": ["MERRA2"],
            "fill_value": -999.0,
            "start": "test",
            "end": "test",
        },
        "messages": [],
        "parameters": {name: {"units": "test", "longname": "test"} for name in series},
    }


class RecordingTransport:
    """A POWER transport that serves one payload and records requested URLs."""

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self.payload = payload
        self.calls: list[str] = []

    def __call__(self, url: str) -> Mapping[str, Any]:
        self.calls.append(url)
        return self.payload


def transport_for(payload: Mapping[str, Any]) -> RecordingTransport:
    """Return a recording transport for one payload."""
    return RecordingTransport(payload)
