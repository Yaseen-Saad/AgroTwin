# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Crop economics: profit ranges, barcode classes and legume credits.

Agent 3 implements this module. Required behaviour (Agent guide §5.7):

    1 - Y_a / Y_m = K_y * (1 - ET_a / ET_c)
    profit = Y_a * P - (C_seed + C_fert + C_labour + C_water * 10 * I_mm) + N_credit * P_N

Every price and cost row must carry ``source_url`` or ``assumption:<tag>`` plus a year. Prices
are never forecast; a price shock is a user input. Barcode classes use
``assumption:amber_margin`` on the window cost.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def profit_per_ha(
    *,
    window_metrics: Mapping[str, Any],
    crop_economics: Sequence[Mapping[str, Any]],
    price_scenario: Mapping[str, float],
) -> dict[str, Any]:
    """Return per-hectare profit with low/base/high price scenarios and source tags."""
    raise NotImplementedError("Agent 3: implement Agent guide §5.7")


def barcode(
    *,
    windows: Sequence[Mapping[str, Any]],
    cost_per_ha: float,
    amber_margin: float,
) -> dict[str, Any]:
    """Return barcode stripes, worst year and loss-year share."""
    raise NotImplementedError(
        "Agent 3: implement barcode classification with assumption:amber_margin"
    )
