# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Every real cache in data/cache must match the frozen site contract."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from contracts.validate import load_assumption_ids, validate_document
from ingest.build_cache import CACHE_DIR
from ingest.serve import load_cached_sites

ASSUMPTIONS = load_assumption_ids()
CACHES = sorted(CACHE_DIR.glob("*.json"))


@pytest.mark.skipif(not CACHES, reason="no generated caches yet; run python -m ingest.build_cache")
@pytest.mark.parametrize("path", CACHES, ids=[path.name for path in CACHES])
def test_generated_cache_is_contract_valid(path) -> None:
    import json

    document = json.loads(path.read_text(encoding="utf-8"))
    assert validate_document("site", document, ASSUMPTIONS) == []


@pytest.mark.skipif(not CACHES, reason="no generated caches yet; run python -m ingest.build_cache")
def test_generated_caches_are_continuous_and_fill_free() -> None:
    documents = load_cached_sites()
    assert len(documents) == 3
    for document in documents:
        daily = document["daily"]
        columns = daily["columns"]
        rows = daily["rows"]
        index = {name: position for position, name in enumerate(columns)}
        start = date.fromisoformat(daily["start"])
        assert date.fromisoformat(rows[0][index["date"]]) == start
        previous = None
        for row in rows:
            current = date.fromisoformat(row[index["date"]])
            if previous is not None:
                assert current == previous + timedelta(days=1)
            previous = current
            assert -999.0 not in row
            precip = row[index["precip_mm"]]
            assert precip is None or precip >= 0
