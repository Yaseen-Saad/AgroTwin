# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The bilingual content library is complete, unique and marked for native review."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
ARABIC = re.compile(r"[\u0600-\u06FF]")


def _load(name: str) -> dict[str, Any]:
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def test_glossary_is_bilingual_and_review_marked() -> None:
    data = _load("glossary.json")
    assert data["needs_native_review"] is True
    assert data["generated_by"]
    terms = data["terms"]
    assert len(terms) >= 15
    ids = [term["id"] for term in terms]
    assert len(ids) == len(set(ids))
    for term in terms:
        assert term["needs_native_review"] is True
        for key in ("en", "ar", "definition_en", "definition_ar"):
            assert term[key].strip()
        assert ARABIC.search(term["ar"]), term["id"]
        assert ARABIC.search(term["definition_ar"]), term["id"]


def test_blindspots_are_bilingual_and_actionable() -> None:
    data = _load("blindspots.json")
    assert data["needs_native_review"] is True
    spots = data["blindspots"]
    assert len(spots) >= 8
    ids = [spot["id"] for spot in spots]
    assert len(ids) == len(set(ids))
    for spot in spots:
        assert spot["severity"] in {"high", "medium"}
        assert spot["needs_native_review"] is True
        for key in (
            "title_en",
            "title_ar",
            "body_en",
            "body_ar",
            "review_action_en",
            "review_action_ar",
        ):
            assert spot[key].strip()
        assert ARABIC.search(spot["title_ar"]), spot["id"]


def test_result_templates_cover_three_advisors_and_three_lenses() -> None:
    data = _load("result_templates.json")
    assert data["needs_native_review"] is True
    assert set(data["advisors"]) >= {
        "agronomist",
        "economist",
        "scientist",
        "scientist_no_scout",
    }
    assert set(data["lens_openings"]) == {"farmer", "investor", "scientist"}
    for advisor in ("agronomist", "economist", "scientist"):
        for language in ("en", "ar"):
            assert data["advisors"][advisor][language].strip()
    for lens in ("farmer", "investor", "scientist"):
        for language in ("en", "ar"):
            assert data["lens_openings"][lens][language].strip()


def test_labels_cover_modes_rotations_and_print_card() -> None:
    data = _load("labels.json")
    assert set(data["mode"]) == {"LIVE", "REPLAY", "SIMULATED", "NONE"}
    assert set(data["rotation"]) >= {"existing", "alt_water", "alt_soil"}
    assert set(data["advisor"]) == {"agronomist", "economist", "scientist"}
    for group in ("mode", "rotation", "advisor", "lens", "unit", "print"):
        for key, entry in data[group].items():
            assert entry["en"].strip(), f"{group}.{key}"
            assert entry["ar"].strip(), f"{group}.{key}"
