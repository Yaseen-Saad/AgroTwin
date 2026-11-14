# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Daily single-crop soil water balance (FAO-56 root-zone depletion method).

Agent 2 implements this module. Required behaviour (Agent guide §5.1):

    TAW = 1000 * (theta_FC - theta_WP) * Z_r
    RAW = p * TAW
    K_s = 1                                  when D_r <= RAW
    K_s = (TAW - D_r) / ((1 - p) * TAW)      when D_r > RAW
    ET_a = K_s * K_c * ET_0
    D_r,i = D_r,i-1 - (P_i - RO_i) - I_i - CR_i + ET_c,i + DP_i

Rules:
- Clamp depletion to 0..TAW; deep percolation occurs above field capacity.
- Irrigated sites refill to field capacity when depletion reaches RAW.
- Rain-fed sites never irrigate.
- Fallow has no transpiration and counts every day as bare.
- Erosion exposure sums rainfall above ``assumption:heavy_rain_mm`` on bare days.
- The water balance must close within 1 mm in the golden test.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from engine.crops import Crop


def daily_water_balance(
    *,
    crop: Crop,
    weather_rows: Sequence[Mapping[str, Any]],
    soil_class: str,
    irrigated: bool,
    irrigation_log: Mapping[str, float] | None = None,
    rain_mult: float = 1.0,
    temp_offset_c: float = 0.0,
) -> dict[str, Any]:
    """Return per-day depletion and the crop-year agronomic metrics.

    The returned mapping must be convertible to one ``window`` object in
    ``contracts/replay.schema.json`` by ``engine.replay``.
    """
    raise NotImplementedError(
        "Agent 2: implement FAO-56 daily water balance per Agent guide §5.1; "
        "see docs/METHODS.md and tests/engine/"
    )
