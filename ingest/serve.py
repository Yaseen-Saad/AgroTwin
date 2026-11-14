# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Cache-first site resolution for the API and the demo.

Order of operations for ``get_site(lat, lon)``:

1. Load the cached demo sites from ``data/cache`` and snap to the nearest one when it is within
   ``MAX_CACHE_SNAP_KM``.
2. Otherwise fetch POWER live with a short timeout (3 s by default).
3. If the live fetch fails, fall back to the nearest cache even if it is far, and say so in the
   resolution note. The demo never blocks on the network.

All returned documents are shaped like ``contracts/site.schema.json``. A live site omits
``irrigation`` and ``soil_class`` because those are field facts the caller has not supplied.
"""

from __future__ import annotations

import json
import logging
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from agrotwin import REPO_ROOT
from ingest.build_cache import DEFAULT_START, default_end
from ingest.power import PowerTransport, fetch_daily

logger = logging.getLogger(__name__)

CACHE_DIR = REPO_ROOT / "data" / "cache"
CACHE_TIMEOUT_S = 3.0
MAX_CACHE_SNAP_KM = 25.0
EARTH_RADIUS_KM = 6371.0088
LIVE_GENERATED_BY = (
    "agent-B / opencode/big-pickle / 2026-11-14 (live POWER fetch for a pinned field)"
)


class SiteUnavailable(RuntimeError):
    """Raised when neither a live fetch nor a cache can serve a pinned field."""


@dataclass(frozen=True)
class SiteResolution:
    """A resolved site document plus how it was obtained."""

    document: dict[str, Any]
    cache_hit: bool
    distance_km: float | None
    fallback_used: bool
    note: str


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two decimal-degree points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, a)))


def load_cached_sites(cache_dir: Path = CACHE_DIR) -> list[dict[str, Any]]:
    """Load every ``*.json`` cache in ``cache_dir``, skipping unreadable files."""
    if not cache_dir.exists():
        return []
    documents: list[dict[str, Any]] = []
    for path in sorted(cache_dir.glob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping unreadable cache %s: %s", path, exc)
            continue
        if isinstance(document, dict) and "lat" in document and "lon" in document:
            documents.append(document)
    return documents


def nearest_cached_site(
    lat: float,
    lon: float,
    cache_dir: Path = CACHE_DIR,
) -> tuple[dict[str, Any] | None, float | None]:
    """Return the nearest cached document and its distance, or ``(None, None)``."""
    best: dict[str, Any] | None = None
    best_distance: float | None = None
    for document in load_cached_sites(cache_dir):
        distance = haversine_km(lat, lon, float(document["lat"]), float(document["lon"]))
        if best_distance is None or distance < best_distance:
            best = document
            best_distance = distance
    return best, best_distance


def _live_site_id(lat: float, lon: float) -> str:
    lat_token = f"{abs(lat):.4f}".replace(".", "p")
    lon_token = f"{abs(lon):.4f}".replace(".", "p")
    lat_sign = "n" if lat >= 0 else "s"
    lon_sign = "e" if lon >= 0 else "w"
    return f"live_{lat_sign}{lat_token}_{lon_sign}{lon_token}"


def build_live_document(
    *,
    lat: float,
    lon: float,
    start: date,
    end: date,
    timeout_s: float = CACHE_TIMEOUT_S,
    transport: PowerTransport | None = None,
) -> dict[str, Any]:
    """Fetch POWER for an arbitrary point and shape a minimal contract-valid site document."""
    daily = fetch_daily(
        lat=lat, lon=lon, start=start, end=end, timeout_s=timeout_s, transport=transport
    )
    return {
        "site_id": _live_site_id(lat, lon),
        "name": f"Live POWER fetch {lat:.4f}, {lon:.4f}",
        "lat": lat,
        "lon": lon,
        "timezone": "UTC",
        "generated_by": LIVE_GENERATED_BY,
        "daily": daily.as_daily_block(),
        "monthly_ndvi": None,
        "monthly_soil_moisture": None,
    }


def resolve_site(
    lat: float,
    lon: float,
    *,
    start: date = DEFAULT_START,
    end: date | None = None,
    timeout_s: float = CACHE_TIMEOUT_S,
    transport: PowerTransport | None = None,
    cache_dir: Path = CACHE_DIR,
) -> SiteResolution:
    """Resolve a pinned field to a cached site or a live POWER document."""
    end = end or default_end()
    cached, distance = nearest_cached_site(lat, lon, cache_dir=cache_dir)
    if cached is not None and distance is not None and distance <= MAX_CACHE_SNAP_KM:
        return SiteResolution(
            document=cached,
            cache_hit=True,
            distance_km=round(distance, 3),
            fallback_used=False,
            note=f"nearest cached site ({distance:.1f} km away)",
        )

    try:
        document = build_live_document(
            lat=lat, lon=lon, start=start, end=end, timeout_s=timeout_s, transport=transport
        )
    except Exception as exc:  # noqa: BLE001 - the demo must never block on the network
        if cached is None:
            raise SiteUnavailable(f"live POWER failed and no cache exists: {exc}") from exc
        logger.warning("Live POWER failed (%s); falling back to the nearest cache", exc)
        assert distance is not None
        return SiteResolution(
            document=cached,
            cache_hit=True,
            distance_km=round(distance, 3),
            fallback_used=True,
            note=f"live POWER failed ({exc}); using nearest cache {distance:.1f} km away",
        )

    return SiteResolution(
        document=document,
        cache_hit=False,
        distance_km=None if distance is None else round(distance, 3),
        fallback_used=False,
        note="live POWER fetch",
    )


def get_site(
    lat: float,
    lon: float,
    *,
    start: date = DEFAULT_START,
    end: date | None = None,
    timeout_s: float = CACHE_TIMEOUT_S,
    transport: PowerTransport | None = None,
    cache_dir: Path = CACHE_DIR,
) -> dict[str, Any]:
    """Return a contract-shaped site document for a pinned field."""
    return resolve_site(
        lat,
        lon,
        start=start,
        end=end,
        timeout_s=timeout_s,
        transport=transport,
        cache_dir=cache_dir,
    ).document


def get_site_by_id(site_id: str, cache_dir: Path = CACHE_DIR) -> dict[str, Any]:
    """Return a cached site by id, or raise :class:`SiteUnavailable`."""
    path = cache_dir / f"{site_id}.json"
    if not path.exists():
        raise SiteUnavailable(f"no cache for site '{site_id}' in {cache_dir}")
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise SiteUnavailable(f"cache for site '{site_id}' is not a JSON object")
    return document


def cache_summary(cache_dir: Path = CACHE_DIR) -> list[dict[str, Any]]:
    """Return a small, JSON-safe inventory of the caches (no rows)."""
    summary: list[dict[str, Any]] = []
    for document in load_cached_sites(cache_dir):
        daily = document.get("daily", {})
        rows = daily.get("rows", []) if isinstance(daily, Mapping) else []
        summary.append(
            {
                "site_id": document.get("site_id"),
                "name": document.get("name"),
                "start": daily.get("start") if isinstance(daily, Mapping) else None,
                "days": len(rows) if isinstance(rows, list) else 0,
                "source": daily.get("source") if isinstance(daily, Mapping) else None,
            }
        )
    return summary
