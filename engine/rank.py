# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Priority-weighted rotation ranking with hard constraints.

Each metric is min-max normalised across the non-excluded rotations with direction-aware scoring:
lower water and erosion are better; higher nitrogen credit, median profit and worst-year profit are
better. The farmer's sliders map to metric groups:

    water -> water use
    soil  -> erosion + nitrogen credit
    money -> median profit + worst-year profit

Hard constraints exclude a rotation with a readable reason. If the top two scores differ by less
than ``assumption:tie_band`` of the score range, the result reports no clear winner.

The returned ``scores`` and ``exclusions`` blocks are for the API and lenses; the frozen result
schema only carries ``weights``, ``order``, ``tie_band_applied`` and ``notes`` inside ``ranking``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from engine.config import assumption_value

SOURCE_TAG = "computed"
GROUP_KEYS = ("water", "soil", "profit")


class RankError(ValueError):
    """Raised when ranking input or weights are incomplete."""


def _number(value: Any, *, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RankError(f"{field} must be numeric, got {value!r}") from exc


def _metric_number(metric: Any, *, field: str) -> float:
    if isinstance(metric, Mapping):
        if "median" in metric:
            return _number(metric["median"], field=field)
        if "value" in metric:
            return _number(metric["value"], field=field)
    return _number(metric, field=field)


def _rotation_values(rotation: Mapping[str, Any]) -> dict[str, float]:
    rotation_id = str(rotation.get("rotation_id", "<unknown>"))
    metrics = rotation.get("metrics")
    if not isinstance(metrics, Mapping):
        raise RankError(f"{rotation_id}: missing metrics block")
    credit = metrics.get("n_credit_kg_ha")
    if isinstance(credit, Mapping):
        credit_mid = (_number(credit.get("low"), field="n_credit.low") + _number(
            credit.get("high"), field="n_credit.high"
        )) / 2.0
    else:
        credit_mid = _number(credit, field="n_credit_kg_ha")
    worst = rotation.get("worst_year")
    if isinstance(worst, Mapping):
        worst_profit = _number(worst.get("profit_per_ha"), field="worst_year.profit_per_ha")
    else:
        worst_profit = _number(worst, field="worst_year")
    return {
        "water_use_mm": _metric_number(metrics.get("water_use_mm"), field="water_use_mm"),
        "erosion_index": _metric_number(metrics.get("erosion_index"), field="erosion_index"),
        "n_credit_kg_ha": credit_mid,
        "profit_per_ha": _metric_number(metrics.get("profit_per_ha"), field="profit_per_ha"),
        "worst_year_profit_per_ha": worst_profit,
        "loss_year_share": _metric_number(
            metrics.get("loss_year_share"), field="loss_year_share"
        ),
    }


def _constraint_reasons(
    rotation: Mapping[str, Any],
    values: Mapping[str, float],
    constraints: Mapping[str, Any],
) -> list[str]:
    reasons: list[str] = []
    rotation_id = str(rotation.get("rotation_id", "<unknown>"))
    excluded = rotation.get("excluded")
    if isinstance(excluded, Mapping) and excluded.get("is_excluded"):
        listed = [str(reason) for reason in excluded.get("reasons", [])]
        reasons.extend(listed or ["marked excluded by the caller"])
    if rotation_id in {str(item) for item in constraints.get("exclude_rotation_ids", ())}:
        reasons.append("excluded by the farmer's rotation-id filter")
    if "max_water_use_mm" in constraints:
        limit = _number(constraints["max_water_use_mm"], field="max_water_use_mm")
        if values["water_use_mm"] > limit:
            reasons.append(f"water use {values['water_use_mm']:.0f} mm exceeds {limit:.0f} mm")
    if "max_erosion_index" in constraints:
        limit = _number(constraints["max_erosion_index"], field="max_erosion_index")
        if values["erosion_index"] > limit:
            reasons.append(
                f"erosion index {values['erosion_index']:.1f} exceeds {limit:.1f}"
            )
    if "min_profit_per_ha" in constraints:
        limit = _number(constraints["min_profit_per_ha"], field="min_profit_per_ha")
        if values["profit_per_ha"] < limit:
            reasons.append(
                f"median profit {values['profit_per_ha']:.0f} EGP/ha is below {limit:.0f}"
            )
    if "min_worst_year_profit_per_ha" in constraints:
        limit = _number(
            constraints["min_worst_year_profit_per_ha"],
            field="min_worst_year_profit_per_ha",
        )
        if values["worst_year_profit_per_ha"] < limit:
            reasons.append(
                "worst-year profit "
                f"{values['worst_year_profit_per_ha']:.0f} EGP/ha is below {limit:.0f}"
            )
    if "max_loss_year_share" in constraints:
        limit = _number(constraints["max_loss_year_share"], field="max_loss_year_share")
        if values["loss_year_share"] > limit:
            reasons.append(
                f"loss-year share {values['loss_year_share']:.2f} exceeds {limit:.2f}"
            )
    if constraints.get("require_legume"):
        crops = rotation.get("crops")
        has_legume = rotation.get("has_legume")
        if has_legume is None and isinstance(crops, Sequence) and not isinstance(crops, str):
            has_legume = any(str(crop) in {"berseem_clover", "faba_bean"} for crop in crops)
        if not has_legume:
            reasons.append("the farmer requires a legume in the rotation")
    return reasons


def _normalise(values: Mapping[str, float], *, higher_better: bool) -> dict[str, float]:
    if not values:
        return {}
    low = min(values.values())
    high = max(values.values())
    if high - low <= 1e-12:
        return {key: 0.5 for key in values}
    if higher_better:
        return {key: (value - low) / (high - low) for key, value in values.items()}
    return {key: 1.0 - (value - low) / (high - low) for key, value in values.items()}


def _weights(weights: Mapping[str, float]) -> dict[str, float]:
    normalised_input = {
        "water": float(weights.get("water", 0.0)),
        "soil": float(weights.get("soil", 0.0)),
        "profit": float(weights.get("profit", weights.get("money", 0.0))),
    }
    for key, value in normalised_input.items():
        if value < 0.0:
            raise RankError(f"weight '{key}' must be non-negative")
    total = sum(normalised_input.values())
    if total <= 0.0:
        raise RankError("at least one weight must be positive")
    return {key: value / total for key, value in normalised_input.items()}


def rank_rotations(
    *,
    rotations: Sequence[Mapping[str, Any]],
    weights: Mapping[str, float],
    constraints: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the ranking block: weights, order, exclusions and tie-band result."""
    if not rotations:
        raise RankError("rotations must contain at least one entry")
    normalised_weights = _weights(weights)
    active_constraints = dict(constraints or {})
    values = {str(row["rotation_id"]): _rotation_values(row) for row in rotations}
    reasons = {
        rotation_id: _constraint_reasons(row, values[rotation_id], active_constraints)
        for row in rotations
        for rotation_id in [str(row["rotation_id"])]
    }
    eligible = [rotation_id for rotation_id in values if not reasons[rotation_id]]
    if not eligible:
        return {
            "weights": normalised_weights,
            "order": [],
            "scores": {},
            "exclusions": reasons,
            "tie_band_applied": False,
            "notes": ["Every rotation is excluded by a hard constraint."],
        }

    water = _normalise(
        {key: values[key]["water_use_mm"] for key in eligible}, higher_better=False
    )
    erosion = _normalise(
        {key: values[key]["erosion_index"] for key in eligible}, higher_better=False
    )
    credit = _normalise(
        {key: values[key]["n_credit_kg_ha"] for key in eligible}, higher_better=True
    )
    profit = _normalise(
        {key: values[key]["profit_per_ha"] for key in eligible}, higher_better=True
    )
    worst = _normalise(
        {key: values[key]["worst_year_profit_per_ha"] for key in eligible},
        higher_better=True,
    )

    scores: dict[str, dict[str, float]] = {}
    for key in eligible:
        soil = (erosion[key] + credit[key]) / 2.0
        money = (profit[key] + worst[key]) / 2.0
        total = (
            normalised_weights["water"] * water[key]
            + normalised_weights["soil"] * soil
            + normalised_weights["profit"] * money
        )
        scores[key] = {
            "water": round(water[key], 6),
            "soil": round(soil, 6),
            "profit": round(money, 6),
            "total": round(total, 6),
        }

    ordered = sorted(eligible, key=lambda key: (-scores[key]["total"], key))
    tie_band = float(assumption_value("tie_band"))
    top = scores[ordered[0]]["total"]
    score_range = top - scores[ordered[-1]]["total"]
    if len(ordered) > 1:
        gap = top - scores[ordered[1]]["total"]
        tie_band_applied = gap <= tie_band * score_range if score_range > 0 else True
    else:
        tie_band_applied = False

    notes = ["Min-max scores computed across the non-excluded rotations."]
    if tie_band_applied:
        notes.append(
            "The top two rotations are within assumption:tie_band; report no clear winner."
        )
    if reasons:
        notes.append("Some rotations were excluded; see the exclusions block.")
    return {
        "weights": normalised_weights,
        "order": ordered,
        "scores": scores,
        "exclusions": reasons,
        "tie_band_applied": tie_band_applied,
        "notes": notes,
    }


def sensitivity(
    *,
    rotations: Sequence[Mapping[str, Any]],
    extremes: Sequence[Mapping[str, float]],
) -> list[dict[str, Any]]:
    """Return rankings under extreme weight sets for QA and the Scientist lens."""
    results: list[dict[str, Any]] = []
    for index, weights in enumerate(extremes):
        try:
            result = rank_rotations(rotations=rotations, weights=weights)
        except RankError as exc:
            raise RankError(f"extreme weight set {index} is invalid: {exc}") from exc
        results.append(
            {
                "weights": result["weights"],
                "order": result["order"],
                "tie_band_applied": result["tie_band_applied"],
            }
        )
    return results
