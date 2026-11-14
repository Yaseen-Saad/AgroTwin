# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""NASA POWER daily point client.

The parameter names below were verified against the live POWER v2 daily point API on
2026-11-14 (``header.api.name == "POWER Daily API"``, ``api.version == "v2.10.3"``) and are
returned by the API's own ``parameters`` metadata block:

    T2M                 Temperature at 2 Meters                  C
    T2M_MIN             Temperature at 2 Meters Minimum          C
    T2M_MAX             Temperature at 2 Meters Maximum          C
    RH2M                Relative Humidity at 2 Meters            %
    WS2M                Wind Speed at 2 Meters                   m/s
    PRECTOTCORR         Precipitation Corrected                 mm/day
    ALLSKY_SFC_SW_DWN   All Sky Surface Shortwave Downward        MJ/m^2/day

Unit mapping to the frozen site contract (``contracts/site.schema.json``):
``tmean_c``, ``tmin_c``, ``tmax_c``, ``precip_mm``, ``rh_pct``, ``wind_ms``,
``solar_mj_m2``. POWER fill values are converted to JSON ``null``; nothing is imputed.

Source tag: ``nasa:POWER``.
"""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_COMMUNITY = "AG"
POWER_FILL_VALUE = -999.0
DEFAULT_TIMEOUT_S = 30.0
USER_AGENT = "AgroTwin/0.1 (NASA Space Apps 2026; cache-first ingest)"

POWER_SOURCE = "nasa:POWER"

# Contract column -> verified POWER parameter name. Order defines the cache column order.
POWER_PARAMETERS: dict[str, str] = {
    "tmean_c": "T2M",
    "tmin_c": "T2M_MIN",
    "tmax_c": "T2M_MAX",
    "precip_mm": "PRECTOTCORR",
    "rh_pct": "RH2M",
    "wind_ms": "WS2M",
    "solar_mj_m2": "ALLSKY_SFC_SW_DWN",
}

CONTRACT_COLUMNS: tuple[str, ...] = ("date", *POWER_PARAMETERS)

PowerTransport = Callable[[str], Mapping[str, Any]]


class PowerDataError(RuntimeError):
    """Raised when the POWER response cannot be parsed or violates physical bounds."""


@dataclass(frozen=True)
class PowerDaily:
    """One cached daily weather block plus provenance diagnostics.

    Attributes:
        start: First requested date.
        rows: ``[date, tmean_c, tmin_c, tmax_c, precip_mm, rh_pct, wind_ms, solar_mj_m2]``
            with POWER fill values replaced by ``None``.
        expected_days: Number of calendar days in the requested range.
        missing_days: ISO dates with no POWER series entry at all.
        missing_values: Count of individual fill/missing parameter values.
        negative_precip_days: ISO dates where POWER returned negative precipitation.
    """

    start: date
    rows: list[list[Any]]
    expected_days: int
    missing_days: tuple[str, ...]
    missing_values: int
    negative_precip_days: tuple[str, ...]

    @property
    def missing_day_share(self) -> float:
        """Share of requested days with no POWER data."""
        return len(self.missing_days) / self.expected_days if self.expected_days else 0.0

    @property
    def missing_value_share(self) -> float:
        """Share of all requested parameter values that were missing or fill."""
        total = self.expected_days * len(POWER_PARAMETERS)
        return self.missing_values / total if total else 0.0

    def as_daily_block(self) -> dict[str, Any]:
        """Return the ``daily`` object required by ``contracts/site.schema.json``."""
        return {
            "source": POWER_SOURCE,
            "start": self.start.isoformat(),
            "columns": list(CONTRACT_COLUMNS),
            "rows": self.rows,
        }


def _iter_days(start: date, end: date) -> Iterator[date]:
    if end < start:
        raise ValueError("end date must not be before start date")
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def build_power_url(*, lat: float, lon: float, start: date, end: date) -> str:
    """Build the POWER daily point URL with the verified parameter catalogue."""
    if not -90.0 <= lat <= 90.0:
        raise ValueError("lat must be within -90..90")
    if not -180.0 <= lon <= 180.0:
        raise ValueError("lon must be within -180..180")
    if end < start:
        raise ValueError("end date must not be before start date")

    query = {
        "parameters": ",".join(POWER_PARAMETERS.values()),
        "community": POWER_COMMUNITY,
        "longitude": f"{lon:.4f}",
        "latitude": f"{lat:.4f}",
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }
    return f"{POWER_API_URL}?{urllib.parse.urlencode(query)}"


def http_get_json(url: str, timeout_s: float = DEFAULT_TIMEOUT_S) -> Mapping[str, Any]:
    """Fetch and decode a JSON document with the standard library.

    Raises:
        OSError: on network failure or timeout (including ``urllib`` errors).
        PowerDataError: when the response body is not a JSON object.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        raw = response.read()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PowerDataError(f"POWER returned a non-JSON body: {exc}") from exc
    if not isinstance(payload, dict):
        raise PowerDataError("POWER response must be a JSON object")
    if payload.get("messages"):
        raise PowerDataError(f"POWER returned messages: {payload['messages']}")
    return payload


def _number_or_none(value: Any, fill_value: float) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number == fill_value:
        return None
    return number


def parse_power_payload(
    payload: Mapping[str, Any],
    *,
    start: date,
    end: date,
) -> PowerDaily:
    """Convert a POWER daily payload into contract-shaped rows.

    Fill values (default ``-999.0`` from ``header.fill_value``) become ``None``. A missing
    series entry becomes ``None``. Missing days are still emitted as all-``null`` rows so the
    date axis stays continuous; the caller reports the missing share instead of imputing.

    Raises:
        PowerDataError: when a required parameter block is absent or rainfall is negative.
    """
    messages = payload.get("messages")
    if messages:
        raise PowerDataError(f"POWER returned messages: {messages}")

    header = payload.get("header", {})
    fill_value = float(header.get("fill_value", POWER_FILL_VALUE)) if header else POWER_FILL_VALUE

    properties = payload.get("properties", {})
    parameter_block = properties.get("parameter") if isinstance(properties, Mapping) else None
    if not isinstance(parameter_block, Mapping):
        raise PowerDataError("POWER response is missing properties.parameter")

    missing_parameters = [
        name for name in POWER_PARAMETERS.values() if name not in parameter_block
    ]
    if missing_parameters:
        raise PowerDataError(f"POWER response is missing parameters: {missing_parameters}")

    series: dict[str, Mapping[str, Any]] = {}
    for column, power_name in POWER_PARAMETERS.items():
        block = parameter_block[power_name]
        if not isinstance(block, Mapping):
            raise PowerDataError(f"POWER parameter {power_name} is not a date->value mapping")
        series[column] = block

    rows: list[list[Any]] = []
    missing_days: list[str] = []
    negative_precip_days: list[str] = []
    missing_values = 0
    for day in _iter_days(start, end):
        key = day.strftime("%Y%m%d")
        day_values: list[Any] = [day.isoformat()]
        day_missing = 0
        for column in POWER_PARAMETERS:
            value = _number_or_none(series[column].get(key), fill_value)
            if value is None:
                day_missing += 1
            elif column == "precip_mm" and value < 0.0:
                negative_precip_days.append(day.isoformat())
            day_values.append(value)
        missing_values += day_missing
        if day_missing == len(POWER_PARAMETERS):
            missing_days.append(day.isoformat())
        rows.append(day_values)

    if negative_precip_days:
        raise PowerDataError(
            "POWER returned negative precipitation on "
            f"{len(negative_precip_days)} day(s), first {negative_precip_days[0]}"
        )

    return PowerDaily(
        start=start,
        rows=rows,
        expected_days=len(rows),
        missing_days=tuple(missing_days),
        missing_values=missing_values,
        negative_precip_days=tuple(negative_precip_days),
    )


def fetch_daily(
    *,
    lat: float,
    lon: float,
    start: date,
    end: date,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    transport: PowerTransport | None = None,
) -> PowerDaily:
    """Fetch NASA POWER daily weather for one point and date range.

    Args:
        lat/lon: decimal degrees; validated against the contract ranges.
        start/end: inclusive UTC dates.
        timeout_s: network timeout; callers that must protect a demo pass ~3 s.
        transport: optional ``url -> payload`` function used by tests instead of the network.

    Returns:
        A :class:`PowerDaily` with nulls for fill values and missing days.

    Raises:
        ValueError: on invalid coordinates or an inverted date range.
        OSError: on network failure or timeout.
        PowerDataError: on a malformed or physically impossible POWER response.
    """
    url = build_power_url(lat=lat, lon=lon, start=start, end=end)
    payload = transport(url) if transport is not None else http_get_json(url, timeout_s)
    return parse_power_payload(payload, start=start, end=end)
