# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""API responses stay contract-valid, mode-tagged and fast on fixtures."""

from __future__ import annotations

import copy
import json
import time

import pytest
from fastapi.testclient import TestClient

from agrotwin import __version__
from contracts.validate import FIXTURES_DIR, load_assumption_ids, load_json, validate_document

ASSUMPTIONS = load_assumption_ids()
TOKEN = "test-scout-token"


def assert_valid_result(document: dict) -> None:
    assert validate_document("result", document, ASSUMPTIONS) == []


def scout_run() -> dict:
    return copy.deepcopy(load_json(FIXTURES_DIR / "scout_run.simulated.json"))


def test_health_reports_version_and_mode(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == __version__
    assert body["schema_version"] == "1.0.0"
    assert body["mode"] == "NONE"
    assert body["engine"] == "fixture"


def test_demo_is_contract_valid_and_labelled(client: TestClient) -> None:
    response = client.get("/demo/delta_01")
    assert response.status_code == 200
    assert response.headers["X-AgroTwin-Mode"] == "SIMULATED"
    assert response.headers["X-AgroTwin-Engine"] == "fixture"
    body = response.json()
    assert_valid_result(body)
    assert body["site_id"] == "delta_01"
    assert body["mode"] == "SIMULATED"
    assert "illustrative" in body["generated_by"]
    assert any("illustrative" in note.lower() for note in body["fusion"]["notes"])


def test_demo_returns_within_three_seconds(client: TestClient) -> None:
    client.get("/demo/delta_01")
    started = time.perf_counter()
    response = client.get("/demo/delta_01")
    elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert elapsed < 3.0, elapsed


def test_unknown_site_is_rejected(client: TestClient) -> None:
    response = client.get("/demo/atlantis_01")
    assert response.status_code == 404
    assert response.json()["detail"]["available_sites"] == ["delta_01"]


def test_diagnose_echoes_scenario_and_filters_rotations(client: TestClient) -> None:
    response = client.post(
        "/diagnose",
        json={
            "site_id": "delta_01",
            "scenario": {"rain_mult": 0.8, "temp_offset_c": 1.5, "price_mult": 1.2},
            "rotation_ids": ["existing"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert_valid_result(body)
    assert body["scenario"] == {"rain_mult": 0.8, "temp_offset_c": 1.5, "price_mult": 1.2}
    assert [item["rotation_id"] for item in body["rotations"]] == ["existing"]
    assert body["ranking"]["order"] == ["existing"]


def test_diagnose_rejects_unknown_rotation(client: TestClient) -> None:
    response = client.post(
        "/diagnose",
        json={"site_id": "delta_01", "rotation_ids": ["rice_monoculture"]},
    )
    assert response.status_code == 422


def test_diagnose_rejects_out_of_range_scenario(client: TestClient) -> None:
    response = client.post(
        "/diagnose",
        json={"site_id": "delta_01", "scenario": {"rain_mult": 9.0}},
    )
    assert response.status_code == 422


def test_simulate_validates_rotation_and_labels_fixture(client: TestClient) -> None:
    rotation = load_json(FIXTURES_DIR / "rotation.existing.json")
    response = client.post(
        "/simulate",
        json={"site_id": "delta_01", "rotations": [rotation], "scenario": {"price_mult": 1.1}},
    )
    assert response.status_code == 200
    body = response.json()
    assert_valid_result(body)
    assert response.headers["X-AgroTwin-Mode"] == "SIMULATED"
    assert response.headers["X-AgroTwin-Request-Rotations"] == "1"
    assert any("not replayed" in note for note in body["fusion"]["notes"])


def test_simulate_rejects_invalid_rotation(client: TestClient) -> None:
    response = client.post(
        "/simulate",
        json={
            "site_id": "delta_01",
            "rotations": [
                {
                    "rotation_id": "broken",
                    "label": "Broken",
                    "slots": [{"year": 1, "season": "winter", "crop": "wheat"}],
                }
            ],
        },
    )
    assert response.status_code == 422
    assert "generated_by" in json.dumps(response.json())


def test_scout_rejects_missing_token_before_parsing_body(client: TestClient) -> None:
    response = client.post(
        "/scout/run",
        content=b"{this is not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401
    assert "token" in response.json()["detail"].lower()


def test_scout_rejects_bad_token(client: TestClient) -> None:
    response = client.post(
        "/scout/run",
        json=scout_run(),
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_scout_accepts_valid_run_and_rejects_duplicate(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    run = scout_run()
    response = client.post("/scout/run", json=run, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["run_id"] == run["run_id"]
    assert body["mode"] == "SIMULATED"
    assert body["n_points"] == len(run["points"])
    assert body["source"] == f"scout:{run['run_id']}"
    assert response.headers["X-AgroTwin-Mode"] == "SIMULATED"

    duplicate = client.post("/scout/run", json=run, headers=auth_headers)
    assert duplicate.status_code == 409


def test_scout_rejects_run_without_mode(client: TestClient, auth_headers: dict[str, str]) -> None:
    run = scout_run()
    run.pop("mode")
    response = client.post("/scout/run", json=run, headers=auth_headers)
    assert response.status_code == 422
    assert "mode" in json.dumps(response.json())


def test_scout_rejects_calibrated_vwc_without_calibration_id(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    run = scout_run()
    run["points"][0]["soil_calibration_id"] = None
    response = client.post("/scout/run", json=run, headers=auth_headers)
    assert response.status_code == 422
    assert "calibration id" in json.dumps(response.json())


def test_scout_intake_is_disabled_without_server_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGROTWIN_SCOUT_TOKEN", raising=False)
    from api.main import app

    with TestClient(app) as no_token_client:
        response = no_token_client.post(
            "/scout/run", json=scout_run(), headers={"Authorization": "Bearer anything"}
        )
    assert response.status_code == 503


def test_calibration_rejects_fewer_than_three_samples(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/scout/calibrate",
        json={"samples": [{"soil_raw": 1000, "vwc_pct": 10}, {"soil_raw": 1500, "vwc_pct": 15}]},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert "3" in response.json()["detail"]


def test_calibration_fits_a_line(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/scout/calibrate",
        json={
            "samples": [
                {"soil_raw": 1000, "vwc_pct": 10.0},
                {"soil_raw": 1500, "vwc_pct": 15.0},
                {"soil_raw": 2000, "vwc_pct": 20.0},
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["calibration_id"].startswith("cal_")
    assert body["n_samples"] == 3
    assert body["slope"] == pytest.approx(0.01)
    assert body["intercept"] == pytest.approx(0.0, abs=1e-6)
    assert body["r2"] == pytest.approx(1.0)
    assert body["source"] == "computed"
    assert response.headers["X-AgroTwin-Mode"] == "NONE"


def test_calibration_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/scout/calibrate",
        json={"samples": [{"soil_raw": 1, "vwc_pct": 1}] * 3},
    )
    assert response.status_code == 401


def test_fieldcard_whatsapp_is_short_and_labelled(client: TestClient) -> None:
    response = client.post("/fieldcard", json={"site_id": "delta_01"})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "SIMULATED"
    assert body["char_count"] == len(body["whatsapp_text"])
    assert body["char_count"] < 600
    assert "SIMULATED" in body["whatsapp_text"]
    assert "not a forecast" in body["whatsapp_text"].lower()
    assert response.headers["X-AgroTwin-Mode"] == "SIMULATED"


def test_feddan_view_is_derived_at_042_hectares(client: TestClient) -> None:
    result = client.get("/demo/delta_01").json()
    response = client.get("/demo/delta_01/feddan")
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "SIMULATED"
    assert body["feddan_in_ha"] == 0.42
    expected = result["rotations"][0]["metrics"]["profit_per_ha"]
    row = body["rotations"][0]
    assert row["profit_per_feddan_egp"]["median"] == pytest.approx(expected["median"] * 0.42)
    assert row["source"] == "computed"
