# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Priority-weighted rotation ranking with hard constraints.

Agent 3 implements this module. Normalise each metric min-max across rotations with
direction-aware scoring (lower water/erosion is better; higher nitrogen credit, median profit and
worst-year profit are better). The farmer's sliders map to metric groups:

    water -> water use
    soil  -> erosion + nitrogen credit
    money -> median profit + worst-year profit

Hard constraints exclude a rotation with a readable reason. If the top two scores differ by less
than ``assumption:tie_band`` of the score range, report no clear winner.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def rank_rotations(
    *,
    rotations: Sequence[Mapping[str, Any]],
    weights: Mapping[str, float],
    constraints: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the ranking block: weights, order, exclusions and tie-band result."""
    raise NotImplementedError("Agent 3: implement Agent guide §5.7 ranking")


def sensitivity(
    *,
    rotations: Sequence[Mapping[str, Any]],
    extremes: Sequence[Mapping[str, float]],
) -> list[dict[str, Any]]:
    """Return rankings under extreme weight sets for QA and the Scientist lens."""
    raise NotImplementedError("Agent 3: implement ranking sensitivity for QA")
