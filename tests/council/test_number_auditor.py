# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Ten seeded bad claims are blocked and ten good claims pass."""

from __future__ import annotations

from typing import Any

import pytest

from council.number_auditor import NumberAuditor

BAD_CLAIMS = (
    "Profit is guaranteed at 4,250 EGP/ha.",
    "Rainfall next year will be 500 mm.",
    "Profit is 9,999 EGP/ha.",
    "Water use is 905 EGP/ha.",
    "Yield will increase by 20%.",
    "The carbon credit is worth 120 USD.",
    "The aquifer health is good at field level.",
    "The sensor is 99.9% accurate.",
    "The Scout guarantees a 30% water saving.",
    "The rainfall forecast is 650 mm.",
)

GOOD_CLAIMS = (
    "The replay covers 8 years.",
    "Median profit is 4,250 EGP/ha.",
    "Water use ranges from 640 to 815 mm/yr.",
    "The worst replayed year is 1992 at -900 EGP/ha.",
    "Loss years are 12.5% of the replay.",
    "ESS is 6.8 and the band narrows to 6,400 EGP/ha.",
    "Scout fusion used 24 points.",
    "The legume credit is 40 to 70 kg N/ha.",
    "The rain multiplier is 1.0.",
    "The ranking gives alt_water a weight of 0.34.",
)


@pytest.mark.parametrize("claim", BAD_CLAIMS)
def test_bad_claim_is_blocked(result: dict[str, Any], claim: str) -> None:
    audit = NumberAuditor(result).check(claim)
    assert not audit.ok, claim
    assert audit.issues
    assert audit.reason


@pytest.mark.parametrize("claim", GOOD_CLAIMS)
def test_good_claim_passes(result: dict[str, Any], claim: str) -> None:
    audit = NumberAuditor(result).check(claim)
    assert audit.ok, f"{claim}\n{audit.issues}"
    assert audit.numbers_checked >= 1


def test_undeclared_source_tag_is_blocked(result: dict[str, Any]) -> None:
    audit = NumberAuditor(result).check("Median profit is 4,250 EGP/ha [assumption:made_up].")
    assert not audit.ok
    assert any(issue.code == "undeclared_source" for issue in audit.issues)


def test_declared_sources_are_returned(result: dict[str, Any]) -> None:
    audit = NumberAuditor(result).check("Water use is 640 to 815 mm/yr. [computed]")
    assert audit.ok
    assert "computed" in audit.sources
