# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Sensor-satellite fusion: re-weight historical years with Scout readings.

Agent 4 implements this module. Required behaviour (Agent guide §5.3):

    w_k proportional to exp(-0.5 * sum_t ((y_t - h_k,t) / sigma)^2)
    ESS = 1 / sum_k(w_k^2)

Gate: refuse without a soil calibration id. On an irrigated site, refuse without an irrigation
log. Guard: if ESS < ``assumption:ess_min``, widen sigma in 10% steps (up to 10 times) and flag
that the range was limited. Bias check: never apply a satellite correction silently.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def fuse(
    *,
    site: Mapping[str, Any],
    replay_result: Mapping[str, Any],
    scout_runs: Sequence[Mapping[str, Any]],
    soil_class: str,
    calibration: Mapping[str, Any],
    irrigation_log: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Return the ``fusion`` block of ``contracts/result.schema.json``.

    Raises:
        ValueError: with a user-facing reason when a gate is not satisfied.
    """
    raise NotImplementedError(
        "Agent 4: implement Agent guide §5.3; refuse without calibration id or irrigation log"
    )
