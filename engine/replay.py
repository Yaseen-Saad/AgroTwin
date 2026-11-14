# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Historical-analog replay orchestration.

Agent 2 implements this module. A replay window starts in historical year ``y`` and runs the
rotation's three years on the actual weather of ``y``, ``y+1`` and ``y+2`` so multi-year
droughts stay intact. Start years run from the first cached year to the last full year minus two.
The output must validate against ``contracts/replay.schema.json``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def run_replay(
    site: Mapping[str, Any],
    rotations: Sequence[Mapping[str, Any]],
    scenario: Mapping[str, float],
    *,
    irrigation_log: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Replay every historical start year for every rotation.

    Args:
        site: A document valid against ``contracts/site.schema.json``.
        rotations: Documents valid against ``contracts/rotation.schema.json``.
        scenario: ``rain_mult``, ``temp_offset_c`` and ``price_mult``.
        irrigation_log: Date -> millimetres for irrigated sites.

    Returns:
        A document valid against ``contracts/replay.schema.json``.
    """
    raise NotImplementedError(
        "Agent 2: implement replay orchestration per Agent guide §5.2; "
        "output must validate against contracts/replay.schema.json"
    )
