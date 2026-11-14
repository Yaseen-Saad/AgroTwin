# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Deterministic two-point-or-more calibration for the Scout soil probe.

Calibration is a linear fit of raw probe counts against gravimetric volumetric water content.
Fewer than three samples is refused: a line through two points has no residual and overstates
confidence.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from typing import Any

MIN_SAMPLES = 3


class CalibrationError(ValueError):
    """Raised when a calibration cannot be produced honestly."""


def fit_calibration(samples: Sequence[tuple[float, float]]) -> dict[str, Any]:
    """Fit ``vwc_pct = slope * soil_raw + intercept`` and return a calibration record.

    Args:
        samples: sequence of ``(soil_raw, vwc_pct)`` pairs.

    Returns:
        A dict with slope, intercept, r2, n_samples and a deterministic calibration id.
    """
    if len(samples) < MIN_SAMPLES:
        raise CalibrationError(f"at least {MIN_SAMPLES} samples are required")
    if any(not math.isfinite(x) or not math.isfinite(y) for x, y in samples):
        raise CalibrationError("samples must be finite numbers")

    n = len(samples)
    sum_x = sum(x for x, _ in samples)
    sum_y = sum(y for _, y in samples)
    mean_x = sum_x / n
    mean_y = sum_y / n
    sxx = sum((x - mean_x) ** 2 for x, _ in samples)
    if sxx == 0.0:
        raise CalibrationError("soil_raw values must not all be identical")
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in samples)
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x

    ss_tot = sum((y - mean_y) ** 2 for _, y in samples)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in samples)
    r2 = 1.0 if ss_tot == 0.0 else max(0.0, 1.0 - ss_res / ss_tot)

    digest = hashlib.sha256(
        "|".join(f"{x:.6f}:{y:.6f}" for x, y in samples).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "calibration_id": f"cal_{digest}",
        "n_samples": n,
        "slope": round(slope, 8),
        "intercept": round(intercept, 6),
        "r2": round(r2, 6),
        "unit": "vwc_percent_per_raw_count",
        "source": "computed",
        "mode": "NONE",
        "note": "Calibration is derived from supplied samples; no Scout run is attached yet.",
    }
