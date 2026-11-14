# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Read the editable assumption ledger.

Every threshold used by the engine must exist in ``engine/config/assumptions.yaml`` before its
``assumption:<id>`` tag appears in code or data. The returned mapping is read-only by convention:
copy values instead of mutating the cache.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from agrotwin import REPO_ROOT

DEFAULT_ASSUMPTIONS_PATH = REPO_ROOT / "engine" / "config" / "assumptions.yaml"


class AssumptionError(KeyError):
    """Raised when an assumption id is missing from the ledger."""


@lru_cache(maxsize=4)
def load_assumptions(path: str | None = None) -> dict[str, dict[str, Any]]:
    """Return the assumption ledger keyed by assumption id."""
    target = Path(path) if path else DEFAULT_ASSUMPTIONS_PATH
    document = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    assumptions = document.get("assumptions")
    if not isinstance(assumptions, dict):
        raise AssumptionError(f"{target} must contain a mapping named 'assumptions'")
    return assumptions


def assumption(assumption_id: str, path: str | None = None) -> dict[str, Any]:
    """Return one assumption record, raising a clear error when it is undeclared."""
    ledger = load_assumptions(path)
    try:
        return ledger[assumption_id]
    except KeyError as exc:
        raise AssumptionError(
            f"unknown assumption '{assumption_id}'; add it to engine/config/assumptions.yaml"
        ) from exc


def assumption_value(assumption_id: str, path: str | None = None) -> Any:
    """Return the primary value of an assumption record."""
    return assumption(assumption_id, path)["value"]
