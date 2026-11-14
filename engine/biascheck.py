# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Satellite soil-moisture bias check against Scout readings.

Agent 4 implements this module. Compare SMAP and Scout values on at least 10 overlapping days,
report the mean gap and never apply a correction unless the user explicitly turns it on. A check
that cannot run returns ``applied: false`` with a reason and is labelled ``not run`` in QA.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def compare_smap(
    *,
    smap_series: Sequence[Mapping[str, Any]],
    scout_readings: Sequence[Mapping[str, Any]],
    apply_correction: bool = False,
) -> dict[str, Any]:
    """Return ``bias_check`` with overlap count, mean gap, applied flag and notes."""
    raise NotImplementedError(
        "Agent 4: implement Agent guide §5.3 step 8; never apply a correction silently"
    )
