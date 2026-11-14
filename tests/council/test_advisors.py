# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Three advisors use templates and always fall back when a provider or audit fails."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

import pytest

from council.advisors import ADVISOR_IDS, ask_council

ARABIC = re.compile(r"[\u0600-\u06FF]")


def test_three_advisors_use_audited_templates(result: dict[str, Any]) -> None:
    replies = ask_council(result, language="en", lens="farmer")
    assert [reply.advisor_id for reply in replies] == list(ADVISOR_IDS)
    for reply in replies:
        assert reply.source == "template"
        assert reply.audit.ok, reply.audit.issues
        assert "[computed]" in reply.text
        assert reply.fallback_reason is None


def test_arabic_advisors_are_bilingual(result: dict[str, Any]) -> None:
    replies = ask_council(result, language="ar", lens="scientist")
    for reply in replies:
        assert reply.audit.ok, reply.audit.issues
        assert ARABIC.search(reply.text), reply.advisor_id


def test_lenses_change_the_opening(result: dict[str, Any]) -> None:
    farmer = ask_council(result, language="en", lens="farmer")
    investor = ask_council(result, language="en", lens="investor")
    assert farmer[0].text != investor[0].text


def test_provider_error_falls_back_to_template(result: dict[str, Any]) -> None:
    def broken(_: str) -> str:
        raise RuntimeError("provider unavailable")

    replies = ask_council(result, language="en", provider=broken)
    for reply in replies:
        assert reply.source == "template"
        assert reply.fallback_reason == "provider_error"
        assert reply.audit.ok


def test_unaudited_provider_text_is_rejected(result: dict[str, Any]) -> None:
    def unsafe(_: str) -> str:
        return "Profit is guaranteed at 4,250 EGP/ha."

    replies = ask_council(result, language="en", provider=unsafe)
    for reply in replies:
        assert reply.source == "template"
        assert reply.fallback_reason is not None
        assert reply.fallback_reason.startswith("audit:")
        assert reply.audit.ok


def test_audited_provider_text_is_kept(result: dict[str, Any]) -> None:
    def safe(_: str) -> str:
        return "The replay shows a median of 4,250 EGP/ha. [computed]"

    replies = ask_council(result, language="en", provider=safe)
    for reply in replies:
        assert reply.source == "provider"
        assert reply.fallback_reason is None
        assert reply.audit.ok


def test_no_scout_uses_the_unfused_template(result: dict[str, Any]) -> None:
    unfused = deepcopy(result)
    unfused["fusion"]["used"] = False
    replies = ask_council(unfused, language="en")
    scientist = next(reply for reply in replies if reply.advisor_id == "scientist")
    assert "No Scout fusion" in scientist.text
    assert scientist.audit.ok


def test_unknown_language_and_lens_are_rejected(result: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        ask_council(result, language="fr")
    with pytest.raises(ValueError):
        ask_council(result, lens="trader")
