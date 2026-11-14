# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""NASA POWER ingest, cache building and cache-first site resolution.

Public modules:

- ``ingest.power`` — verified POWER daily point client and fill-value handling.
- ``ingest.build_cache`` — writes ``data/cache/<site_id>.json`` for the demo sites.
- ``ingest.serve`` — nearest cached site, live fetch with a 3 s timeout, cache fallback.
- ``ingest.appeears`` — optional AppEEARS NDVI/soil-moisture extract; nulls when unavailable.
"""

from __future__ import annotations

from ingest.power import (
    CONTRACT_COLUMNS,
    POWER_PARAMETERS,
    PowerDaily,
    PowerDataError,
    fetch_daily,
)

__all__ = [
    "CONTRACT_COLUMNS",
    "POWER_PARAMETERS",
    "PowerDaily",
    "PowerDataError",
    "fetch_daily",
]
