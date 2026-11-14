# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Load and validate ``engine/crops.yaml``.

The catalogue is provisional until Agent 2 verifies every coefficient and an agronomist reviews
the Egyptian planting windows. Coefficients that are not yet cited must be tagged as assumptions
before they are used in a result.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agrotwin import REPO_ROOT

DEFAULT_CROPS_PATH = REPO_ROOT / "engine" / "crops.yaml"
SEASONS = {"winter", "summer", "any"}
STAGE_KEYS = ("initial", "development", "mid", "late")
KC_KEYS = ("initial", "mid", "late")


class CropError(ValueError):
    """Raised when the crop catalogue is malformed or internally inconsistent."""


@dataclass(frozen=True)
class Crop:
    """One crop's agronomic parameters."""

    crop_id: str
    label: str
    family: str
    season: str
    stages_days: dict[str, int]
    kc: dict[str, float]
    root_depth_m: float
    depletion_fraction: float
    ky: float
    n_credit_low: float
    n_credit_high: float
    n_credit_source: str
    planting_window: dict[str, str] | None

    @property
    def total_days(self) -> int:
        """Total crop-stage length in days."""
        return sum(self.stages_days.values())

    @property
    def is_legume(self) -> bool:
        """True when the crop contributes a nitrogen credit."""
        return self.n_credit_high > 0


@dataclass(frozen=True)
class CropCatalog:
    """Validated crop catalogue with its provenance metadata."""

    version: str
    review_status: str
    citations: dict[str, str]
    crops: dict[str, Crop]

    def get(self, crop_id: str) -> Crop:
        """Return one crop or raise a clear error."""
        try:
            return self.crops[crop_id]
        except KeyError as exc:
            raise CropError(f"unknown crop '{crop_id}'; add it to engine/crops.yaml") from exc

    @property
    def ids(self) -> tuple[str, ...]:
        """Crop ids in catalogue order."""
        return tuple(self.crops)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CropError(message)


def _parse_crop(crop_id: str, raw: dict[str, Any]) -> Crop:
    _require(isinstance(raw, dict), f"crop '{crop_id}' must be a mapping")
    for key in (
        "label",
        "family",
        "season",
        "stages_days",
        "kc",
        "root_depth_m",
        "depletion_fraction",
        "ky",
        "n_credit_kg_ha",
    ):
        _require(key in raw, f"crop '{crop_id}' is missing '{key}'")

    season = str(raw["season"])
    _require(season in SEASONS, f"crop '{crop_id}' has invalid season '{season}'")

    stages = raw["stages_days"]
    _require(isinstance(stages, dict), f"crop '{crop_id}' stages_days must be a mapping")
    stages_clean: dict[str, int] = {}
    for key in STAGE_KEYS:
        value = stages.get(key)
        _require(isinstance(value, int) and value >= 0, f"crop '{crop_id}' stage '{key}' invalid")
        stages_clean[key] = value
    total_days = sum(stages_clean.values())
    if crop_id != "fallow":
        _require(total_days > 0, f"crop '{crop_id}' must have a positive stage length")

    kc = raw["kc"]
    _require(isinstance(kc, dict), f"crop '{crop_id}' kc must be a mapping")
    kc_clean: dict[str, float] = {}
    for key in KC_KEYS:
        value = kc.get(key)
        _require(
            isinstance(value, (int, float)) and 0.0 <= float(value) <= 2.0,
            f"crop '{crop_id}' kc '{key}' must be within 0..2",
        )
        kc_clean[key] = float(value)

    root_depth = float(raw["root_depth_m"])
    depletion = float(raw["depletion_fraction"])
    ky = float(raw["ky"])
    _require(root_depth >= 0.0, f"crop '{crop_id}' root_depth_m must be non-negative")
    _require(0.0 <= depletion <= 1.0, f"crop '{crop_id}' depletion_fraction must be within 0..1")
    _require(0.0 <= ky <= 2.0, f"crop '{crop_id}' ky must be within 0..2")

    credit = raw["n_credit_kg_ha"]
    _require(isinstance(credit, dict), f"crop '{crop_id}' n_credit_kg_ha must be a mapping")
    low = float(credit.get("low", 0))
    high = float(credit.get("high", 0))
    _require(0.0 <= low <= high, f"crop '{crop_id}' nitrogen credit requires 0 <= low <= high")
    if high > 0:
        source = raw.get("n_credit_source")
        _require(
            isinstance(source, str) and source.startswith("assumption:"),
            f"legume '{crop_id}' needs an assumption:<id> nitrogen-credit source",
        )
    else:
        source = "computed"

    window = raw.get("planting_window")
    if window is not None:
        _require(
            isinstance(window, dict) and "start" in window and "end" in window,
            f"crop '{crop_id}' planting_window needs start and end",
        )
        window = {"start": str(window["start"]), "end": str(window["end"])}

    return Crop(
        crop_id=crop_id,
        label=str(raw["label"]),
        family=str(raw["family"]),
        season=season,
        stages_days=stages_clean,
        kc=kc_clean,
        root_depth_m=root_depth,
        depletion_fraction=depletion,
        ky=ky,
        n_credit_low=low,
        n_credit_high=high,
        n_credit_source=str(source),
        planting_window=window,
    )


def load_crops(path: str | Path | None = None) -> CropCatalog:
    """Load and validate the crop catalogue from YAML."""
    target = Path(path) if path else DEFAULT_CROPS_PATH
    document = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    raw_crops = document.get("crops")
    _require(isinstance(raw_crops, dict) and raw_crops, f"{target} must define a 'crops' mapping")

    crops = {crop_id: _parse_crop(crop_id, raw) for crop_id, raw in raw_crops.items()}
    _require("fallow" in crops, "the catalogue must define 'fallow'")
    return CropCatalog(
        version=str(document.get("version", "0.0.0")),
        review_status=str(document.get("review_status", "unknown")),
        citations=dict(document.get("citations", {})),
        crops=crops,
    )


_CATALOGUE: CropCatalog | None = None


def default_catalogue() -> CropCatalog:
    """Return the process-wide catalogue, loaded once."""
    global _CATALOGUE
    if _CATALOGUE is None:
        _CATALOGUE = load_crops()
    return _CATALOGUE
