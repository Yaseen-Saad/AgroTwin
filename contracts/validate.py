# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Validate AgroTwin contract fixtures against JSON Schema and cross-field invariants.

Usage:
    python -m contracts.validate --all
    python -m contracts.validate --schema result
    python -m contracts.validate --fixture result.delta_01.json

The JSON Schemas cannot express row/column alignment, percentile ordering, barcode
consistency or assumption-tag membership, so those checks live here. Exit code 1 means
the build must stop.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT / "contracts"
FIXTURES_DIR = CONTRACTS_DIR / "fixtures"
ASSUMPTIONS_FILE = ROOT / "engine" / "config" / "assumptions.yaml"
VERSION_FILE = ROOT / "VERSION"

SCHEMA_FILES: dict[str, Path] = {
    "site": CONTRACTS_DIR / "site.schema.json",
    "rotation": CONTRACTS_DIR / "rotation.schema.json",
    "scout_run": CONTRACTS_DIR / "scout_run.schema.json",
    "replay": CONTRACTS_DIR / "replay.schema.json",
    "result": CONTRACTS_DIR / "result.schema.json",
}

FIXTURES: dict[str, list[str]] = {
    "site": ["site.delta_01.json"],
    "rotation": [
        "rotation.existing.json",
        "rotation.alt_water.json",
        "rotation.alt_soil.json",
    ],
    "scout_run": ["scout_run.simulated.json"],
    "replay": ["replay.delta_01.json"],
    "result": ["result.delta_01.json"],
}

RANGE_METRIC_KEYS = {
    "water_use_mm",
    "deficit_days",
    "bare_days",
    "erosion_index",
    "profit_per_ha",
}


def load_json(path: Path) -> Any:
    """Read UTF-8 JSON from path."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_repo_version() -> str:
    """Return the single-source repository version."""
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def load_assumption_ids() -> set[str]:
    """Return every assumption id declared in engine/config/assumptions.yaml."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise SystemExit(
            "PyYAML is required: python -m pip install -r requirements-dev.txt"
        ) from exc

    if not ASSUMPTIONS_FILE.exists():
        raise SystemExit(f"Missing assumptions file: {ASSUMPTIONS_FILE}")
    document = yaml.safe_load(ASSUMPTIONS_FILE.read_text(encoding="utf-8")) or {}
    assumptions = document.get("assumptions", {})
    if not isinstance(assumptions, dict):
        raise SystemExit("assumptions.yaml must contain a mapping named 'assumptions'")
    return set(assumptions)


def iter_strings(value: Any) -> list[str]:
    """Yield every string nested in a JSON-like value."""
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(iter_strings(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(iter_strings(item))
    return found


def check_assumption_tags(document: Any, assumption_ids: set[str]) -> list[str]:
    """Every assumption:<id> tag must exist in the assumptions file."""
    errors: list[str] = []
    for text in iter_strings(document):
        if text.startswith("assumption:"):
            tag_id = text.split(":", 1)[1]
            if tag_id not in assumption_ids:
                errors.append(f"unknown assumption tag '{text}' (add it to assumptions.yaml)")
    return errors


def check_site(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    daily = document["daily"]
    columns: list[str] = daily["columns"]
    rows: list[list[Any]] = daily["rows"]
    width = len(columns)
    index = {name: position for position, name in enumerate(columns)}
    seen_dates: set[str] = set()
    previous: date | None = None

    for row_number, row in enumerate(rows, start=1):
        if len(row) != width:
            errors.append(f"daily.rows[{row_number}] has {len(row)} values, expected {width}")
            continue
        raw_date = row[index["date"]]
        if not isinstance(raw_date, str):
            errors.append(f"daily.rows[{row_number}] date must be a string")
            continue
        try:
            parsed = date.fromisoformat(raw_date)
        except ValueError:
            errors.append(f"daily.rows[{row_number}] invalid date '{raw_date}'")
            continue
        if raw_date in seen_dates:
            errors.append(f"daily.rows[{row_number}] duplicate date '{raw_date}'")
        seen_dates.add(raw_date)
        if previous is not None and parsed <= previous:
            errors.append(f"daily.rows[{row_number}] dates must be strictly increasing")
        previous = parsed

        precip = row[index["precip_mm"]]
        if isinstance(precip, (int, float)) and precip < 0:
            errors.append(f"daily.rows[{row_number}] negative precipitation")
        tmin, tmean, tmax = (
            row[index["tmin_c"]],
            row[index["tmean_c"]],
            row[index["tmax_c"]],
        )
        if all(isinstance(v, (int, float)) for v in (tmin, tmean, tmax)):
            if not (tmin <= tmean <= tmax):
                errors.append(f"daily.rows[{row_number}] requires tmin <= tmean <= tmax")
    return errors


def check_rotation(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[tuple[int, str]] = set()
    per_year: dict[int, int] = {}
    for slot in document["slots"]:
        key = (slot["year"], slot["season"])
        if key in seen:
            errors.append(f"duplicate slot for year {slot['year']} {slot['season']}")
        seen.add(key)
        per_year[slot["year"]] = per_year.get(slot["year"], 0) + 1
    for year, count in sorted(per_year.items()):
        if count > 2:
            errors.append(f"year {year} has {count} seasons; at most 2 are allowed")
    return errors


def check_scout_run(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    stamps: list[datetime] = []
    for point_number, point in enumerate(document["points"], start=1):
        try:
            stamps.append(datetime.fromisoformat(point["t"].replace("Z", "+00:00")))
        except (KeyError, ValueError):
            errors.append(f"points[{point_number}] has an invalid timestamp")
        lat, lon = point.get("lat"), point.get("lon")
        if (lat is None) != (lon is None):
            errors.append(f"points[{point_number}] lat and lon must both be set or both null")
        if point.get("soil_vwc_pct") is not None and not point.get("soil_calibration_id"):
            errors.append(
                f"points[{point_number}] reports calibrated VWC without a calibration id"
            )
    if any(later < earlier for earlier, later in zip(stamps, stamps[1:], strict=False)):
        errors.append("points must be ordered by timestamp")
    return errors


def check_replay(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rotation_ids: set[str] = set()
    for rotation in document["rotations"]:
        rotation_id = rotation["rotation_id"]
        if rotation_id in rotation_ids:
            errors.append(f"duplicate rotation_id '{rotation_id}'")
        rotation_ids.add(rotation_id)
        starts: set[int] = set()
        for window in rotation["windows"]:
            if window["start_year"] in starts:
                errors.append(f"duplicate start_year {window['start_year']} in '{rotation_id}'")
            starts.add(window["start_year"])
            expected = [window["start_year"], window["start_year"] + 1, window["start_year"] + 2]
            if window["years"] != expected:
                errors.append(
                    f"window {window['start_year']} in '{rotation_id}' "
                    "must span three consecutive years"
                )
            credit = window["n_credit_kg_ha"]
            if credit["low"] > credit["high"]:
                errors.append(f"window {window['start_year']} in '{rotation_id}' has low > high")
    return errors


def check_result(document: dict[str, Any], assumption_ids: set[str]) -> list[str]:
    errors: list[str] = []
    repo_version = load_repo_version()
    if document["version"] != repo_version:
        errors.append(f"result.version '{document['version']}' != VERSION '{repo_version}'")

    years = document["years"]
    if years != sorted(years):
        errors.append("result.years must be sorted ascending")
    year_set = set(years)

    rotation_ids: set[str] = set()
    included_ids: set[str] = set()
    for rotation in document["rotations"]:
        rid = rotation["rotation_id"]
        if rid in rotation_ids:
            errors.append(f"duplicate rotation_id '{rid}'")
        rotation_ids.add(rid)
        excluded = rotation["excluded"]["is_excluded"]
        if not excluded:
            included_ids.add(rid)

        metrics = rotation["metrics"]
        for key in RANGE_METRIC_KEYS:
            metric = metrics[key]
            if not (metric["p10"] <= metric["median"] <= metric["p90"]):
                errors.append(f"{rid}.{key} requires p10 <= median <= p90")
        credit = metrics["n_credit_kg_ha"]
        if credit["low"] > credit["high"]:
            errors.append(f"{rid}.n_credit_kg_ha requires low <= high")
        if not 0 <= metrics["loss_year_share"]["value"] <= 1:
            errors.append(f"{rid}.metrics.loss_year_share must be within 0..1")

        stripes = rotation["barcode"]
        stripe_years = [stripe["year"] for stripe in stripes]
        if len(stripe_years) != len(set(stripe_years)):
            errors.append(f"{rid}.barcode has duplicate years")
        if not set(stripe_years).issubset(year_set):
            errors.append(f"{rid}.barcode years must be a subset of result.years")
        for stripe in stripes:
            if stripe["class"] == "red" and stripe["profit_per_ha"] >= 0:
                errors.append(f"{rid}.barcode {stripe['year']} is red but profit is not negative")
            if stripe["class"] != "red" and stripe["profit_per_ha"] < 0:
                errors.append(f"{rid}.barcode {stripe['year']} is not red but profit is negative")

        worst = rotation["worst_year"]
        if stripe_years:
            lowest = min(stripes, key=lambda stripe: stripe["profit_per_ha"])
            if worst["year"] != lowest["year"] or worst["profit_per_ha"] != lowest["profit_per_ha"]:
                errors.append(f"{rid}.worst_year does not match the lowest barcode stripe")
        red_share = sum(1 for stripe in stripes if stripe["class"] == "red") / len(stripes)
        if abs(red_share - rotation["loss_year_share"]["value"]) > 1e-9:
            errors.append(f"{rid}.loss_year_share does not match the barcode red share")
        if abs(rotation["loss_year_share"]["value"] - metrics["loss_year_share"]["value"]) > 1e-9:
            errors.append(f"{rid}.loss_year_share disagrees with metrics.loss_year_share")

    fusion = document["fusion"]
    if document["mode"] == "NONE" and fusion["used"]:
        errors.append("mode NONE cannot use scout data")
    if fusion["used"] and document["mode"] == "NONE":
        errors.append("fusion.used is true but mode is NONE")
    if fusion["used"]:
        if not fusion["scout_run_ids"]:
            errors.append("fusion.used requires at least one scout_run_id")
        if fusion["n_points"] <= 0:
            errors.append("fusion.used requires n_points > 0")
        if fusion["sigma_used"] <= 0:
            errors.append("fusion.used requires sigma_used > 0")
        if fusion["range_width"]["with_scout"] > fusion["range_width"]["without_scout"]:
            errors.append("fusion.range_width.with_scout must not exceed without_scout")
        if fusion["ess"] < 1:
            errors.append("fusion.ess must be at least 1 when fusion is used")
    weights = fusion["weights_by_year"]
    if weights:
        if not set(weights).issubset({str(year) for year in years}):
            errors.append("fusion.weights_by_year keys must be years present in result.years")
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 1e-6:
            errors.append(f"fusion.weights_by_year must sum to 1.0 (got {weight_sum:.6f})")

    ranking = document["ranking"]
    weight_sum = sum(ranking["weights"].values())
    if abs(weight_sum - 1.0) > 1e-6:
        errors.append(f"ranking.weights must sum to 1.0 (got {weight_sum:.6f})")
    order = ranking["order"]
    if set(order) != included_ids:
        errors.append("ranking.order must contain exactly the non-excluded rotation ids")
    if len(order) != len(set(order)):
        errors.append("ranking.order must not contain duplicates")

    for assumption in document.get("assumptions", []):
        expected = f"assumption:{assumption['id']}"
        if assumption["source"] != expected:
            errors.append(f"assumption '{assumption['id']}' must use source '{expected}'")
        if assumption["id"] not in assumption_ids:
            errors.append(f"assumption '{assumption['id']}' is not declared in assumptions.yaml")
    return errors


CROSS_CHECKS = {
    "site": lambda doc, _: check_site(doc),
    "rotation": lambda doc, _: check_rotation(doc),
    "scout_run": lambda doc, _: check_scout_run(doc),
    "replay": lambda doc, _: check_replay(doc),
    "result": lambda doc, ids: check_result(doc, ids),
}


def validate_fixture(kind: str, fixture_name: str, assumption_ids: set[str]) -> list[str]:
    """Validate one fixture and return a list of human-readable errors."""
    schema = load_json(SCHEMA_FILES[kind])
    document = load_json(FIXTURES_DIR / fixture_name)
    errors: list[str] = []

    declared_version = schema.get("x-schema-version")
    if not declared_version:
        errors.append("schema is missing x-schema-version")
    if kind in {"result", "replay", "site", "scout_run", "rotation"}:
        if isinstance(document, dict) and "schema_version" in document:
            if document["schema_version"] != declared_version:
                errors.append(
                    f"schema_version '{document['schema_version']}' != schema '{declared_version}'"
                )

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{location}: {error.message}")

    errors.extend(check_assumption_tags(document, assumption_ids))
    errors.extend(CROSS_CHECKS[kind](document, assumption_ids))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="validate every fixture (default)")
    group.add_argument(
        "--schema", choices=sorted(SCHEMA_FILES), help="validate fixtures of one schema"
    )
    group.add_argument("--fixture", help="validate one fixture file name")
    args = parser.parse_args(argv)

    assumption_ids = load_assumption_ids()
    selected: list[tuple[str, str]] = []
    if args.fixture:
        matches = [
            (kind, name)
            for kind, names in FIXTURES.items()
            for name in names
            if name == args.fixture
        ]
        if not matches:
            parser.error(f"unknown fixture '{args.fixture}'")
        selected = matches
    elif args.schema:
        selected = [(args.schema, name) for name in FIXTURES[args.schema]]
    else:
        selected = [(kind, name) for kind, names in FIXTURES.items() for name in names]

    failures = 0
    for kind, name in selected:
        errors = validate_fixture(kind, name, assumption_ids)
        if errors:
            failures += 1
            print(f"FAIL  {kind:10s} {name}")
            for error in errors:
                print(f"      - {error}")
        else:
            print(f"OK    {kind:10s} {name}")

    print(f"\n{len(selected) - failures}/{len(selected)} fixtures valid")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
