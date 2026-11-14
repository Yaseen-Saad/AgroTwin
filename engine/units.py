# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Unit conversions at the engine/API boundary.

The engine stores hectares, millimetres and EGP. The API adds per-feddan values for the Farmer
lens. One feddan is defined as 0.42 hectares (about 4,200 m²); the constant is part of the
contract and must not be duplicated elsewhere.
"""

from __future__ import annotations

FEDDAN_IN_HA = 0.42
M2_PER_HA = 10_000.0
M2_PER_FEDDAN = M2_PER_HA * FEDDAN_IN_HA


def ha_to_feddan(hectares: float) -> float:
    """Convert hectares to feddans."""
    return hectares / FEDDAN_IN_HA


def feddan_to_ha(feddans: float) -> float:
    """Convert feddans to hectares."""
    return feddans * FEDDAN_IN_HA


def mm_to_m3_per_ha(depth_mm: float) -> float:
    """Convert a water depth in mm over one hectare to cubic metres."""
    return depth_mm * 10.0


def mm_to_m3_per_feddan(depth_mm: float) -> float:
    """Convert a water depth in mm over one feddan to cubic metres."""
    return depth_mm * 10.0 * FEDDAN_IN_HA


def egp_per_ha_to_feddan(value_per_ha: float) -> float:
    """Convert an EGP-per-hectare amount to EGP per feddan."""
    return value_per_ha * FEDDAN_IN_HA


def egp_per_feddan_to_ha(value_per_feddan: float) -> float:
    """Convert an EGP-per-feddan amount to EGP per hectare."""
    return value_per_feddan / FEDDAN_IN_HA
