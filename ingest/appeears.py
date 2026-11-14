# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Optional NASA AppEEARS extract for monthly NDVI and soil moisture.

AppEEARS is an asynchronous task API that needs an Earthdata login. This MVP treats it as an
optional, fail-closed layer: without credentials, or without an enabled extract, the site cache
ships ``monthly_ndvi: null`` and ``monthly_soil_moisture: null``. No satellite value is ever
invented, and POWER weather is never blocked by an AppEEARS failure.

Credentials are read from the environment only (``EARTHDATA_USERNAME`` /
``EARTHDATA_PASSWORD``) and are never written to disk.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date

logger = logging.getLogger(__name__)

EARTHDATA_USERNAME_ENV = "EARTHDATA_USERNAME"
EARTHDATA_PASSWORD_ENV = "EARTHDATA_PASSWORD"

NO_CREDENTIALS_NOTE = (
    "Earthdata credentials are not set; monthly NDVI and soil moisture are null "
    "(POWER-only fallback)."
)
NOT_ENABLED_NOTE = (
    "AppEEARS extract is not enabled in the MVP; monthly NDVI and soil moisture are null."
)


@dataclass(frozen=True)
class MonthlyIndices:
    """Optional monthly satellite indices plus the honest reason they are missing."""

    monthly_ndvi: dict[str, object] | None
    monthly_soil_moisture: dict[str, object] | None
    note: str

    @property
    def available(self) -> bool:
        """True when at least one satellite product was retrieved."""
        return self.monthly_ndvi is not None or self.monthly_soil_moisture is not None


def credentials_configured(
    environ: dict[str, str] | None = None,
) -> bool:
    """Return True only when both Earthdata environment variables are non-empty."""
    source = os.environ if environ is None else environ
    return bool(source.get(EARTHDATA_USERNAME_ENV)) and bool(source.get(EARTHDATA_PASSWORD_ENV))


def fetch_monthly_indices(
    *,
    lat: float,
    lon: float,
    start: date,
    end: date,
    environ: dict[str, str] | None = None,
) -> MonthlyIndices:
    """Return the optional satellite indices or explicit nulls with a reason.

    This function never raises for a missing credential: the demo must continue on POWER
    weather alone. When credentials exist but the extract is not enabled, it returns nulls and
    says so rather than fabricating a product.
    """
    del lat, lon, start, end  # reserved for the AppEEARS task geometry once enabled
    if not credentials_configured(environ):
        logger.info("AppEEARS skipped: %s", NO_CREDENTIALS_NOTE)
        return MonthlyIndices(None, None, NO_CREDENTIALS_NOTE)
    logger.info("AppEEARS skipped: %s", NOT_ENABLED_NOTE)
    return MonthlyIndices(None, None, NOT_ENABLED_NOTE)
