# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Build schema-valid site caches from NASA POWER daily weather.

Usage::

    python -m ingest.build_cache                       # 1991-01-01 .. last complete year
    python -m ingest.build_cache --sites delta_01
    python -m ingest.build_cache --start 1991-01-01 --end 2025-12-31

The demo coordinates and site attributes come from ``SPEC.md`` §5. Power is historical and
near-real-time only; this module never produces a forecast. Optional AppEEARS indices are
null unless a real extract is enabled (see ``ingest.appeears``).

Output: ``data/cache/<site_id>.json``, UTF-8, two-space indent, trailing newline, matching
``contracts/site.schema.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from agrotwin import REPO_ROOT
from ingest.appeears import fetch_monthly_indices
from ingest.power import POWER_PARAMETERS, PowerTransport, fetch_daily

CACHE_DIR = REPO_ROOT / "data" / "cache"
DEFAULT_START = date(1991, 1, 1)
GENERATED_BY = (
    "agent-B / opencode/big-pickle / 2026-11-14 "
    "(NASA POWER daily point API; real reanalysis weather, fill values null)"
)


@dataclass(frozen=True)
class DemoLocation:
    """One demo site from ``SPEC.md`` §5."""

    site_id: str
    name: str
    lat: float
    lon: float
    elevation_m: float | None
    irrigation: str
    soil_class: str
    timezone: str


DEMO_LOCATIONS: tuple[DemoLocation, ...] = (
    DemoLocation(
        site_id="delta_01",
        name="Mansoura, Nile Delta",
        lat=31.0409,
        lon=31.3785,
        elevation_m=8.0,
        irrigation="irrigated",
        soil_class="clay_loam",
        timezone="Africa/Cairo",
    ),
    DemoLocation(
        site_id="matruh_01",
        name="Marsa Matruh hinterland",
        lat=31.3543,
        lon=27.2373,
        elevation_m=30.0,
        irrigation="rainfed",
        soil_class="sandy_loam",
        timezone="Africa/Cairo",
    ),
    DemoLocation(
        site_id="sevilla_01",
        name="Seville, Andalusia, Spain",
        lat=37.3891,
        lon=-5.9845,
        elevation_m=10.0,
        irrigation="rainfed",
        soil_class="clay_loam",
        timezone="Europe/Madrid",
    ),
)

LOCATIONS_BY_ID: dict[str, DemoLocation] = {site.site_id: site for site in DEMO_LOCATIONS}


def last_complete_year(today: date | None = None) -> int:
    """Return the last calendar year that is fully in the past."""
    reference = today or date.today()
    return reference.year - 1


def default_end(today: date | None = None) -> date:
    """Return December 31 of the last complete calendar year."""
    return date(last_complete_year(today), 12, 31)


def build_site_document(
    location: DemoLocation,
    *,
    start: date = DEFAULT_START,
    end: date | None = None,
    timeout_s: float = 30.0,
    transport: PowerTransport | None = None,
) -> dict[str, object]:
    """Return one site-cache document ready for ``contracts/site.schema.json``."""
    end = end or default_end()
    daily = fetch_daily(
        lat=location.lat,
        lon=location.lon,
        start=start,
        end=end,
        timeout_s=timeout_s,
        transport=transport,
    )
    indices = fetch_monthly_indices(lat=location.lat, lon=location.lon, start=start, end=end)
    return {
        "site_id": location.site_id,
        "name": location.name,
        "lat": location.lat,
        "lon": location.lon,
        "elevation_m": location.elevation_m,
        "irrigation": location.irrigation,
        "soil_class": location.soil_class,
        "timezone": location.timezone,
        "generated_by": GENERATED_BY,
        "daily": daily.as_daily_block(),
        "monthly_ndvi": indices.monthly_ndvi,
        "monthly_soil_moisture": indices.monthly_soil_moisture,
    }


def write_cache(document: dict[str, object], *, out_dir: Path = CACHE_DIR) -> Path:
    """Write a site cache atomically with deterministic JSON formatting."""
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{document['site_id']}.json"
    serialized = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(serialized, encoding="utf-8")
    temporary.replace(target)
    return target


def build_caches(
    *,
    site_ids: list[str] | None = None,
    start: date = DEFAULT_START,
    end: date | None = None,
    out_dir: Path = CACHE_DIR,
    timeout_s: float = 30.0,
    transport: PowerTransport | None = None,
) -> list[dict[str, object]]:
    """Build and write caches for the selected demo sites, returning a JSON summary."""
    if end is None:
        end = default_end()
    selected = site_ids or [site.site_id for site in DEMO_LOCATIONS]
    unknown = [site_id for site_id in selected if site_id not in LOCATIONS_BY_ID]
    if unknown:
        raise ValueError(f"unknown site id(s): {unknown}; known: {sorted(LOCATIONS_BY_ID)}")

    summaries: list[dict[str, object]] = []
    for site_id in selected:
        location = LOCATIONS_BY_ID[site_id]
        document = build_site_document(
            location, start=start, end=end, timeout_s=timeout_s, transport=transport
        )
        target = write_cache(document, out_dir=out_dir)
        daily = document["daily"]
        assert isinstance(daily, dict)
        rows = daily["rows"]
        assert isinstance(rows, list)
        expected_days = len(rows)
        missing_days = sum(1 for row in rows if all(value is None for value in row[1:]))
        missing_values = sum(
            1 for row in rows for value in row[1:] if value is None
        )
        total_values = expected_days * len(POWER_PARAMETERS)
        summaries.append(
            {
                "site_id": site_id,
                "path": str(target),
                "start": start.isoformat(),
                "end": end.isoformat(),
                "days": expected_days,
                "missing_days": missing_days,
                "missing_day_share": (
                    round(missing_days / expected_days, 6) if expected_days else 0.0
                ),
                "missing_values": missing_values,
                "missing_value_share": (
                    round(missing_values / total_values, 6) if total_values else 0.0
                ),
                "monthly_ndvi": document["monthly_ndvi"],
                "monthly_soil_moisture": document["monthly_soil_moisture"],
                "source": "nasa:POWER",
            }
        )
    return summaries


def parse_date(value: str) -> date:
    """Parse an ISO date for the CLI."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid ISO date '{value}'") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build NASA POWER site caches")
    parser.add_argument("--start", type=parse_date, default=DEFAULT_START)
    parser.add_argument(
        "--end",
        type=parse_date,
        default=None,
        help="inclusive end date; defaults to 31 December of the last complete year",
    )
    parser.add_argument(
        "--sites",
        nargs="+",
        choices=sorted(LOCATIONS_BY_ID),
        default=None,
        help="site ids to build; defaults to all three demo sites",
    )
    parser.add_argument("--out", type=Path, default=CACHE_DIR)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    end = args.end or default_end()
    if end < args.start:
        parser.error("--end must not be before --start")

    summaries = build_caches(
        site_ids=args.sites,
        start=args.start,
        end=end,
        out_dir=args.out,
        timeout_s=args.timeout,
    )
    print(json.dumps({"caches": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
