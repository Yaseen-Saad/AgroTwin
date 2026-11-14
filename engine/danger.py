# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Robust danger-window detection for the field diagnosis timeline.

Agent 2 implements this module. For every day-of-year and variable (rainfall, maximum
temperature, modelled wetness, cached NDVI) compute a 15-day baseline median and MAD across all
years, then:

    z_d = (x_d - median_d) / (1.4826 * MAD_d)

Flag a window when ``abs(z) > assumption:danger_z`` for at least ``assumption:danger_min_days``
consecutive days. Thresholds are editable in ``engine/config/assumptions.yaml``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def danger_windows(site: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return flagged danger windows with variable, date range, peak z-score and source tag."""
    raise NotImplementedError(
        "Agent 2: implement Agent guide §5.6; read thresholds from engine/config/assumptions.yaml"
    )
