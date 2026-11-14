# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Soil water constants used by the FAO-56 root-zone balance.

Values come from ``engine/config/soil_classes.yaml`` (FAO-56 Table 19, provisional
transcription). The loader is intentionally small: the engine needs field capacity and wilting
point in volumetric fractions, and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from agrotwin import REPO_ROOT

DEFAULT_SOIL_PATH = REPO_ROOT / "engine" / "config" / "soil_classes.yaml"


class SoilClassError(ValueError):
    """Raised when a soil class is missing or malformed."""


@dataclass(frozen=True)
class SoilClass:
    """Volumetric water content at field capacity and wilting point (m3/m3)."""

    name: str
    theta_fc: float
    theta_wp: float

    @property
    def available_water_fraction(self) -> float:
        """Readily stored water between wilting point and field capacity (m3/m3)."""
        return self.theta_fc - self.theta_wp


@lru_cache(maxsize=4)
def load_soil_classes(path: str | None = None) -> dict[str, SoilClass]:
    """Load every soil class from YAML, keyed by the contract enum value."""
    target = Path(path) if path else DEFAULT_SOIL_PATH
    document = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    raw = document.get("soil_classes")
    if not isinstance(raw, dict) or not raw:
        raise SoilClassError(f"{target} must contain a mapping named 'soil_classes'")

    classes: dict[str, SoilClass] = {}
    for name, entry in raw.items():
        if not isinstance(entry, dict) or "theta_fc" not in entry or "theta_wp" not in entry:
            raise SoilClassError(f"soil class '{name}' needs theta_fc and theta_wp")
        theta_fc = float(entry["theta_fc"])
        theta_wp = float(entry["theta_wp"])
        if not 0.0 <= theta_wp < theta_fc <= 1.0:
            raise SoilClassError(
                f"soil class '{name}' requires 0 <= theta_wp < theta_fc <= 1 "
                f"(got {theta_wp}, {theta_fc})"
            )
        classes[str(name)] = SoilClass(str(name), theta_fc, theta_wp)
    return classes


def get_soil_class(name: str, path: str | None = None) -> SoilClass:
    """Return one soil class or raise a clear error."""
    try:
        return load_soil_classes(path)[name]
    except KeyError as exc:
        raise SoilClassError(
            f"unknown soil class '{name}'; expected one of {sorted(load_soil_classes(path))}"
        ) from exc
