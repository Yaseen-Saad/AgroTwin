# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""AgroTwin FastAPI service.

Gate 1 serves contract-valid fixtures with explicit ``SIMULATED`` labels. Scout intake and
calibration are real; replay, fusion and economics arrive from the Builder behind the same
result schema. Run with ``python -m uvicorn api.main:app``.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from agrotwin import __version__
from api.auth import require_scout_token
from api.calibrate import MIN_SAMPLES, CalibrationError, fit_calibration
from api.demo import (
    ASSUMPTION_IDS,
    DEMO_SITES,
    DemoSiteUnavailable,
    demo_result,
    fieldcard,
    fixture_result,
    per_feddan_view,
)
from contracts.validate import validate_document

MAX_SCOUT_BODY_BYTES = 1_000_000
MODE_HEADER = "X-AgroTwin-Mode"
ENGINE_HEADER = "X-AgroTwin-Engine"
ScoutAuth = Annotated[None, Depends(require_scout_token)]


def _tag(response: Response, mode: str) -> None:
    response.headers[MODE_HEADER] = mode
    response.headers[ENGINE_HEADER] = "fixture"


def _require_demo_site(site_id: str) -> None:
    if site_id not in DEMO_SITES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"no demo result fixture for site '{site_id}' yet",
                "available_sites": list(DEMO_SITES),
            },
        )


class ScenarioInput(BaseModel):
    """Scenario multipliers accepted by diagnose and simulate."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    rain_mult: float = Field(default=1.0, ge=0.0, le=3.0)
    temp_offset_c: float = Field(default=0.0, ge=-10.0, le=10.0)
    price_mult: float = Field(default=1.0, ge=0.0, le=5.0)

    def as_dict(self) -> dict[str, float]:
        return {
            "rain_mult": self.rain_mult,
            "temp_offset_c": self.temp_offset_c,
            "price_mult": self.price_mult,
        }


class DiagnoseRequest(BaseModel):
    """A site, optional scenario and optional subset of demo rotations."""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_]*$")
    scenario: ScenarioInput = Field(default_factory=ScenarioInput)
    rotation_ids: list[str] | None = Field(default=None, max_length=3)


class SimulateRequest(BaseModel):
    """Rotation documents to validate now and replay when the engine lands."""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_]*$")
    rotations: list[dict[str, Any]] = Field(min_length=1, max_length=3)
    scenario: ScenarioInput = Field(default_factory=ScenarioInput)


class SiteRequest(BaseModel):
    """One site id for a field card."""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_]*$")


class CalibrationSample(BaseModel):
    """One gravimetric calibration pair."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    soil_raw: float = Field(ge=0.0)
    vwc_pct: float = Field(ge=0.0, le=100.0)


class CalibrationRequest(BaseModel):
    """Calibration samples posted by the bridge after oven-drying."""

    model_config = ConfigDict(extra="forbid")

    samples: list[CalibrationSample] = Field(min_length=1, max_length=200)


def create_app() -> FastAPI:
    """Create the FastAPI application with Scout intake state."""
    service = FastAPI(
        title="AgroTwin API",
        version=__version__,
        description=(
            "Fixture-backed Gate 1 API. Every result carries mode and source tags. "
            "Scout intake requires a bearer token."
        ),
    )
    origins = [
        item.strip()
        for item in os.environ.get(
            "AGROTWIN_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        ).split(",")
        if item.strip()
    ]
    service.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    service.state.scout_runs = {}

    @service.get("/")
    def root() -> dict[str, Any]:
        return {
            "service": "agrotwin-api",
            "version": __version__,
            "mode": "NONE",
            "docs": "/docs",
            "health": "/health",
            "demo": f"/demo/{DEMO_SITES[0]}",
        }

    @service.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "schema_version": fixture_result()["schema_version"],
            "mode": "NONE",
            "engine": "fixture",
            "sites": list(DEMO_SITES),
            "note": "Fixture-backed Gate 1 build; engine replay pending.",
        }

    @service.get("/demo/{site_id}")
    def demo(site_id: str, response: Response) -> dict[str, Any]:
        _require_demo_site(site_id)
        result = demo_result(site_id=site_id)
        _tag(response, result["mode"])
        response.headers["Cache-Control"] = "public, max-age=60"
        return result

    @service.get("/demo/{site_id}/feddan")
    def demo_feddan(site_id: str, response: Response) -> dict[str, Any]:
        _require_demo_site(site_id)
        result = demo_result(site_id=site_id)
        _tag(response, result["mode"])
        return per_feddan_view(result)

    @service.post("/diagnose")
    def diagnose(body: DiagnoseRequest, response: Response) -> dict[str, Any]:
        _require_demo_site(body.site_id)
        known = {rotation["rotation_id"] for rotation in fixture_result()["rotations"]}
        if body.rotation_ids is not None:
            unknown = sorted(set(body.rotation_ids) - known)
            if unknown:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={"message": "unknown demo rotation ids", "rotation_ids": unknown},
                )
        try:
            result = demo_result(
                site_id=body.site_id,
                scenario=body.scenario.as_dict(),
                rotation_ids=body.rotation_ids,
            )
        except DemoSiteUnavailable as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        _tag(response, result["mode"])
        return result

    @service.post("/simulate")
    def simulate(body: SimulateRequest, response: Response) -> dict[str, Any]:
        _require_demo_site(body.site_id)
        errors: list[str] = []
        for index, rotation in enumerate(body.rotations):
            for error in validate_document("rotation", rotation, ASSUMPTION_IDS):
                errors.append(f"rotations[{index}]: {error}")
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"message": "rotation contract violation", "errors": errors},
            )
        result = demo_result(site_id=body.site_id, scenario=body.scenario.as_dict())
        result["fusion"]["notes"].append(
            "Requested rotations were validated but not replayed: the engine is pending. "
            "The response shows the illustrative demo rotations."
        )
        _tag(response, result["mode"])
        response.headers["X-AgroTwin-Request-Rotations"] = str(len(body.rotations))
        return result

    @service.post("/scout/run", status_code=status.HTTP_201_CREATED)
    async def submit_scout_run(
        request: Request,
        response: Response,
        _: ScoutAuth,
    ) -> dict[str, Any]:
        declared = request.headers.get("content-length")
        if declared is not None and int(declared) > MAX_SCOUT_BODY_BYTES:
            raise HTTPException(status_code=413, detail="Scout run body is too large")
        raw = await request.body()
        if len(raw) > MAX_SCOUT_BODY_BYTES:
            raise HTTPException(status_code=413, detail="Scout run body is too large")
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(status_code=400, detail="Scout run body must be JSON") from exc

        errors = validate_document("scout_run", payload, ASSUMPTION_IDS)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"message": "scout_run contract violation", "errors": errors},
            )

        run_id = payload["run_id"]
        runs: dict[str, Any] = request.app.state.scout_runs
        if run_id in runs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scout run '{run_id}' already exists",
            )
        runs[run_id] = payload
        response.headers[MODE_HEADER] = payload["mode"]
        return {
            "ok": True,
            "run_id": run_id,
            "site_id": payload["site_id"],
            "mode": payload["mode"],
            "n_points": len(payload["points"]),
            "source": f"scout:{run_id}",
            "accepted_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        }

    @service.post("/scout/calibrate", status_code=status.HTTP_201_CREATED)
    def calibrate(
        body: CalibrationRequest,
        response: Response,
        _: ScoutAuth,
    ) -> dict[str, Any]:
        if len(body.samples) < MIN_SAMPLES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"at least {MIN_SAMPLES} calibration samples are required",
            )
        try:
            record = fit_calibration([(item.soil_raw, item.vwc_pct) for item in body.samples])
        except CalibrationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
            ) from exc
        response.headers[MODE_HEADER] = record["mode"]
        return record

    @service.post("/fieldcard")
    def field_card(body: SiteRequest, response: Response) -> dict[str, Any]:
        _require_demo_site(body.site_id)
        result = demo_result(site_id=body.site_id)
        card = fieldcard(result)
        _tag(response, card["mode"])
        return card

    return service


app = create_app()


