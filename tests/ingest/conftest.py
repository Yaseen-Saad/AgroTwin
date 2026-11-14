# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Shared fixtures for ingest tests: demo location, three-day range and temp cache dir."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ingest.build_cache import DEMO_LOCATIONS, DemoLocation


@pytest.fixture()
def three_days() -> tuple[date, date]:
    return date(2020, 1, 1), date(2020, 1, 3)


@pytest.fixture()
def demo_location() -> DemoLocation:
    return DEMO_LOCATIONS[0]


@pytest.fixture()
def cache_dir(tmp_path: Path) -> Path:
    target = tmp_path / "cache"
    target.mkdir()
    return target
