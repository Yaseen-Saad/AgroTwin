# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Fixture-backed demo results with an explicit honesty label.

Only ``delta_01`` has a result fixture at Gate 1. The helper never invents a site result: it
reuses the illustrative fixture, relabels ``generated_by``, adds a note, and re-validates the
document against ``contracts/result.schema.json`` before the API can return it.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any

from contracts.validate import (
    FIXTURES_DIR,
    load_assumption_ids,
    load_json,
    validate_document,
)

DEMO_SITE_ID = "delta_01"
DEMO_SITES: tuple[str, ...] = (DEMO_SITE_ID,)
RESULT_FIXTURE = FIXTURES_DIR / "result.delta_01.json"
ASSUMPTION_IDS = load_assumption_ids()
FIXTURE_NOTE = (
    "Fixture-backed API response: engine replay is pending, so these numbers are illustrative "
    "and are not a site result."
)
GENERATED_BY = (
    "api / opencode/big-pickle / 2026-11-14 "
    "(fixture-backed Gate 1 demo; illustrative, not a real site result)"
)


class DemoSiteUnavailable(LookupError):
    """Raised when a site has no demo fixture yet."""


@lru_cache(maxsize=1)
def fixture_result() -> dict[str, Any]:
    """Return the illustrative result fixture (read once)."""
    return load_json(RESULT_FIXTURE)


def _scenario_tuple(scenario: dict[str, float] | None) -> tuple[float, float, float]:
    source = scenario or fixture_result()["scenario"]
    return (
        float(source["rain_mult"]),
        float(source["temp_offset_c"]),
        float(source["price_mult"]),
    )


@lru_cache(maxsize=32)
def _build(
    site_id: str,
    scenario_key: tuple[float, float, float],
    rotation_ids: tuple[str, ...] | None,
    mode: str,
) -> dict[str, Any]:
    if site_id not in DEMO_SITES:
        raise DemoSiteUnavailable(site_id)

    document = deepcopy(fixture_result())
    document["site_id"] = site_id
    document["mode"] = mode
    document["generated_by"] = GENERATED_BY
    document["scenario"] = {
        "rain_mult": scenario_key[0],
        "temp_offset_c": scenario_key[1],
        "price_mult": scenario_key[2],
    }

    if rotation_ids is not None:
        selected = [item for item in document["rotations"] if item["rotation_id"] in rotation_ids]
        if not selected:
            raise DemoSiteUnavailable("no requested rotation exists in the demo fixture")
        document["rotations"] = selected
        included = {item["rotation_id"] for item in selected if not item["excluded"]["is_excluded"]}
        document["ranking"]["order"] = [
            rotation_id for rotation_id in document["ranking"]["order"] if rotation_id in included
        ]

    notes = document["fusion"].setdefault("notes", [])
    if FIXTURE_NOTE not in notes:
        notes.append(FIXTURE_NOTE)

    errors = validate_document("result", document, ASSUMPTION_IDS)
    if errors:
        raise RuntimeError(f"fixture-backed result violates the contract: {errors}")
    return document


def demo_result(
    *,
    site_id: str = DEMO_SITE_ID,
    scenario: dict[str, float] | None = None,
    rotation_ids: list[str] | None = None,
    mode: str = "SIMULATED",
) -> dict[str, Any]:
    """Return a contract-valid demo result for one site."""
    key = tuple(rotation_ids) if rotation_ids is not None else None
    return deepcopy(_build(site_id, _scenario_tuple(scenario), key, mode))


def per_feddan_view(result: dict[str, Any]) -> dict[str, Any]:
    """Return a derived per-feddan profit view for the Farmer lens.

    The engine stores EGP per hectare; the API adds per-feddan values at 0.42 ha per feddan.
    This view is derived, tagged ``computed`` and is not part of the frozen result contract.
    """
    from engine.units import FEDDAN_IN_HA

    rotations: list[dict[str, Any]] = []
    for rotation in result["rotations"]:
        profit = rotation["metrics"]["profit_per_ha"]
        rotations.append(
            {
                "rotation_id": rotation["rotation_id"],
                "label": rotation["label"],
                "profit_per_feddan_egp": {
                    "p10": round(profit["p10"] * FEDDAN_IN_HA, 2),
                    "median": round(profit["median"] * FEDDAN_IN_HA, 2),
                    "p90": round(profit["p90"] * FEDDAN_IN_HA, 2),
                },
                "source": "computed",
            }
        )
    return {
        "site_id": result["site_id"],
        "mode": result["mode"],
        "unit": "EGP_per_feddan",
        "feddan_in_ha": FEDDAN_IN_HA,
        "rotations": rotations,
        "note": "Derived view at 0.42 ha per feddan; the frozen result contract stays per hectare.",
    }


def fieldcard(result: dict[str, Any]) -> dict[str, Any]:
    """Build a short, source-tagged Field Card and WhatsApp message from a result."""
    water = result["rotations"][0]["metrics"]["water_use_mm"]
    profit = result["rotations"][0]["metrics"]["profit_per_ha"]
    whatsapp = (
        f"AgroTwin · {result['site_id']} · {result['mode']} fixture\n"
        f"Water range {water['p10']}-{water['p90']} mm/yr (computed, illustrative).\n"
        f"Profit range {profit['p10']} to {profit['p90']} EGP/ha, "
        f"median {profit['median']} (computed, illustrative).\n"
        "A range is not a forecast. Fixture-backed demo; engine replay pending.\n"
        "Sources: computed from the illustrative fixture."
    )
    return {
        "site_id": result["site_id"],
        "mode": result["mode"],
        "generated_by": GENERATED_BY,
        "headline": "Three rotations, shown as ranges. Not a forecast.",
        "whatsapp_text": whatsapp,
        "char_count": len(whatsapp),
        "sections": [
            {
                "title": "Water",
                "lines": [
                    f"p10 {water['p10']} · median {water['median']} · "
                    f"p90 {water['p90']} mm/yr"
                ],
                "sources": [water["source"]],
            },
            {
                "title": "Profit",
                "lines": [
                    f"p10 {profit['p10']} · median {profit['median']} · p90 {profit['p90']} EGP/ha"
                ],
                "sources": [profit["source"]],
            },
        ],
        "disclaimer": "Illustrative fixture. Not a site result and not a promise of outcome.",
    }
