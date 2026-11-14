# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The Field Card is short, audited, printable and carries a local QR."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from council.field_card import make_field_card
from council.number_auditor import NumberAuditor


@pytest.mark.parametrize("language", ["en", "ar"])
def test_whatsapp_text_is_under_limit(result: dict[str, Any], language: str) -> None:
    card = make_field_card(result, language)
    assert card.length < 600
    assert card.mode in card.whatsapp_text or language == "ar"
    assert "[computed]" in card.whatsapp_text
    assert NumberAuditor(result).check(card.whatsapp_text).ok


@pytest.mark.parametrize("language", ["en", "ar"])
def test_qr_is_generated_locally(result: dict[str, Any], language: str) -> None:
    card = make_field_card(result, language)
    assert card.qr_svg.startswith("<svg")
    assert "qrline" in card.qr_svg


def test_print_card_is_directional_and_has_no_logo_image(result: dict[str, Any]) -> None:
    english = make_field_card(result, "en")
    arabic = make_field_card(result, "ar")
    assert 'dir="ltr"' in english.print_html
    assert 'dir="rtl"' in arabic.print_html
    assert "SIMULATED" in english.print_html
    assert "<img" not in english.print_html
    assert "guaranteed" not in english.print_html.lower()
    assert "qrline" in english.print_html


def test_unfused_card_omits_the_scout_line(result: dict[str, Any]) -> None:
    unfused = deepcopy(result)
    unfused["fusion"]["used"] = False
    card = make_field_card(unfused, "en")
    assert "Scout:" not in card.whatsapp_text
    assert NumberAuditor(unfused).check(card.whatsapp_text).ok


def test_unknown_language_is_rejected(result: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        make_field_card(result, "fr")
