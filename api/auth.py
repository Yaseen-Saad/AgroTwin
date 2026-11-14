# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Bearer-token gate for Scout intake.

The token comes from ``AGROTWIN_SCOUT_TOKEN`` only. The dependency runs before the route reads
the body, so an unauthenticated request is rejected before JSON parsing.
"""

from __future__ import annotations

import os
import secrets

from fastapi import Header, HTTPException, status

TOKEN_ENV = "AGROTWIN_SCOUT_TOKEN"


def configure_token() -> str:
    """Return the configured token or raise a 503 when intake is disabled."""
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Scout intake disabled: set {TOKEN_ENV} on the server",
        )
    return token


def require_scout_token(authorization: str | None = Header(default=None)) -> None:
    """Reject a missing or wrong bearer token before the body is parsed."""
    expected = configure_token()
    scheme, _, supplied = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not supplied:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Scout bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Scout bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
