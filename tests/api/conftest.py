# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""API test client with a known Scout token and a clean in-memory run store."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

TOKEN = "test-scout-token"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AGROTWIN_SCOUT_TOKEN", TOKEN)
    from api.main import app

    app.state.scout_runs.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.state.scout_runs.clear()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TOKEN}"}
