# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Shared fixture for Council, Number Auditor and Field Card tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
RESULT_FIXTURE = ROOT / "contracts" / "fixtures" / "result.delta_01.json"


@pytest.fixture(scope="session")
def result() -> dict[str, Any]:
    return json.loads(RESULT_FIXTURE.read_text(encoding="utf-8"))
