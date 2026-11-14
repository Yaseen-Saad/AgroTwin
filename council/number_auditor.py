# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The Number Auditor blocks promises, undeclared numbers and unit-mismatched claims."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .text import normalize_unit

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

NUMBER_RE = re.compile(
    r"(?<![\w.])"
    r"(?P<number>[-+]?\d[\d,]*(?:\.\d+)?)"
    r"(?:\s*(?P<unit>"
    r"%"
    r"|mm(?:\s*/\s*(?:yr|year|سنة|عام))?"
    r"|egp(?:\s*/\s*ha)?"
    r"|usd(?:\s*/\s*ha)?"
    r"|kg\s*n?\s*/\s*ha"
    r"|days?(?:\s*/\s*(?:yr|year))?"
    r"|years?"
    r"|feddan"
    r"|ha"
    r"|هكتار"
    r"|فدان"
    r"|يوم"
    r"|أيام"
    r"|سنة"
    r"|سنوات"
    r"|مم(?:\s*/\s*(?:سنة|عام))?"
    r"|كغ\s*ن?\s*/\s*هكتار"
    r"|مؤشر"
    r"))?",
    re.IGNORECASE,
)

SOURCE_TAG_RE = re.compile(r"\[([^\[\]]+)\]")

FORBIDDEN_EN = (
    (re.compile(r"\bguarantee(?:d|s)?\b", re.IGNORECASE), "promise"),
    (re.compile(r"\bwill\b", re.IGNORECASE), "promise"),
    (re.compile(r"\bcertain(?:ly)?\b", re.IGNORECASE), "promise"),
    (re.compile(r"\bno risk\b", re.IGNORECASE), "promise"),
    (re.compile(r"\bforecast\b", re.IGNORECASE), "forecast"),
    (re.compile(r"\bpredict(?:ion|ed|s)?\b", re.IGNORECASE), "forecast"),
    (re.compile(r"\brainfall (?:next|forecast|prediction)\b", re.IGNORECASE), "forecast"),
    (re.compile(r"\bcarbon credit\b", re.IGNORECASE), "carbon"),
    (re.compile(r"\baquifer (?:health|level)\b", re.IGNORECASE), "aquifer"),
    (re.compile(r"\brevenue\b", re.IGNORECASE), "revenue"),
)

FORBIDDEN_AR = (
    (re.compile(r"سوف"), "promise"),
    (re.compile(r"سيضمن|تضمن|مضمون|بالتأكيد|مؤكد"), "promise"),
    (re.compile(r"تنبؤ"), "forecast"),
    (re.compile(r"توقع\s+المطر"), "forecast"),
    (re.compile(r"ائتمان\s+كربون"), "carbon"),
    (re.compile(r"صحة\s+الخزان\s+الجوفي"), "aquifer"),
)

@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    token: str


@dataclass(frozen=True)
class AuditResult:
    ok: bool
    issues: tuple[Issue, ...]
    numbers_checked: int
    sources: tuple[str, ...]

    @property
    def reason(self) -> str:
        return "; ".join(sorted({issue.code for issue in self.issues}))


@dataclass(frozen=True)
class AllowedNumber:
    value: float
    unit: str | None
    source: str
    path: str


def _clean_text(text: str, result: dict[str, Any]) -> str:
    """Remove identifiers and disclosed negations before scanning for claims."""
    cleaned = text.translate(ARABIC_DIGITS)
    cleaned = re.sub(r"\bnot (?:a )?(?:forecast|prediction)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("ليست تنبؤاً", "").replace("ليس تنبؤاً", "")
    for identifier in [result.get("site_id", "")] + [
        rotation.get("rotation_id", "") for rotation in result.get("rotations", [])
    ]:
        if identifier:
            cleaned = cleaned.replace(str(identifier), "")
    return cleaned


def _unit_matches(allowed: str | None, claimed: str | None) -> bool:
    if claimed is None:
        return True
    return allowed == claimed


class NumberAuditor:
    """Audit a Council sentence against the numbers and source tags declared by one result."""

    def __init__(self, result: dict[str, Any]) -> None:
        self.result = result
        self.allowed: tuple[AllowedNumber, ...] = tuple(self._collect_allowed())
        self.allowed_sources = {entry.source for entry in self.allowed} | {"computed", "scenario"}

    def _collect_allowed(self) -> Iterable[AllowedNumber]:
        seen: set[tuple[float, str | None]] = set()

        def add(value: Any, unit: str | None, source: str, path: str) -> None:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return
            number = float(value)
            normalized = normalize_unit(unit)
            variants = {number, round(number, 0), round(number, 1), round(number, 2)}
            for variant in variants:
                key = (round(variant, 6), normalized)
                if key not in seen:
                    seen.add(key)
                    queue.append(AllowedNumber(float(variant), normalized, source, path))
            if normalized == "fraction":
                for variant in {number * 100, round(number * 100, 0), round(number * 100, 1)}:
                    key = (round(variant, 6), "%")
                    if key not in seen:
                        seen.add(key)
                        queue.append(AllowedNumber(float(variant), "%", source, f"{path}.percent"))

        queue: list[AllowedNumber] = []
        scenario = self.result.get("scenario", {})
        for key, value in scenario.items():
            add(value, None, "scenario", f"scenario.{key}")

        years = self.result.get("years", [])
        add(len(years), "year", "computed", "years.count")
        for year in years:
            add(year, "year", "computed", "years.item")

        rotations = self.result.get("rotations", [])
        add(len(rotations), "rotation", "computed", "rotations.count")
        for rotation in rotations:
            prefix = f"rotations.{rotation.get('rotation_id')}"
            for name, metric in rotation.get("metrics", {}).items():
                if not isinstance(metric, dict):
                    continue
                unit = metric.get("currency") or metric.get("unit")
                source = str(metric.get("source", "computed"))
                for key in ("p10", "median", "p90", "low", "high", "value"):
                    if key in metric:
                        add(metric[key], unit, source, f"{prefix}.metrics.{name}.{key}")
            for stripe in rotation.get("barcode", []):
                add(
                    stripe.get("profit_per_ha"),
                    stripe.get("currency"),
                    "computed",
                    f"{prefix}.barcode",
                )
                add(stripe.get("year"), "year", "computed", f"{prefix}.barcode.year")
            worst = rotation.get("worst_year", {})
            add(worst.get("profit_per_ha"), worst.get("currency"), "computed", f"{prefix}.worst")
            add(worst.get("year"), "year", "computed", f"{prefix}.worst.year")

        fusion = self.result.get("fusion", {})
        add(fusion.get("n_points"), "point", "computed", "fusion.n_points")
        add(fusion.get("ess"), None, "computed", "fusion.ess")
        add(fusion.get("sigma_used"), None, "computed", "fusion.sigma_used")
        add(fusion.get("bias_check", {}).get("n_overlap_days"), "day", "computed", "fusion.overlap")
        for year, weight in fusion.get("weights_by_year", {}).items():
            add(weight, "weight", "computed", f"fusion.weights.{year}")
        range_width = fusion.get("range_width", {})
        for key in ("without_scout", "with_scout"):
            add(
                range_width.get(key),
                range_width.get("unit"),
                "computed",
                f"fusion.{key}",
            )

        sightings = self.result.get("scout_summary", {}).get("sightings", {})
        for key, value in sightings.items():
            add(value, "point", "computed", f"scout.{key}")

        for key, value in self.result.get("ranking", {}).get("weights", {}).items():
            add(value, "weight", "computed", f"ranking.weights.{key}")

        for assumption in self.result.get("assumptions", []):
            add(
                assumption.get("value"),
                None,
                str(assumption.get("source", "computed")),
                "assumptions",
            )

        while queue:
            yield queue.pop(0)

    def check(self, text: str) -> AuditResult:
        """Return an audit result; any issue means the caller must use fixed templates."""
        cleaned = _clean_text(text, self.result)
        issues: list[Issue] = []

        for pattern, code in FORBIDDEN_EN + FORBIDDEN_AR:
            match = pattern.search(cleaned)
            if match:
                issues.append(
                    Issue(
                        code=f"forbidden_{code}",
                        message=f"forbidden {code} wording",
                        token=match.group(0),
                    )
                )

        matched_sources: set[str] = set()
        checked = 0
        for match in NUMBER_RE.finditer(cleaned):
            raw = match.group("number")
            if not raw:
                continue
            checked += 1
            raw = raw.replace(",", "")
            try:
                value = float(raw)
            except ValueError:
                continue
            claimed_unit = normalize_unit(match.group("unit"))
            candidates = [
                entry
                for entry in self.allowed
                if abs(entry.value - value) <= 0.0005 and _unit_matches(entry.unit, claimed_unit)
            ]
            same_value = [entry for entry in self.allowed if abs(entry.value - value) <= 0.0005]
            if candidates:
                matched_sources.update(entry.source for entry in candidates)
                continue
            if same_value:
                units = sorted({str(entry.unit) for entry in same_value})
                issues.append(
                    Issue(
                        code="mismatched_unit",
                        message=f"number exists with unit(s) {units}, not {claimed_unit}",
                        token=match.group(0).strip(),
                    )
                )
            else:
                issues.append(
                    Issue(
                        code="undeclared_number",
                        message="number is not declared by the result",
                        token=match.group(0).strip(),
                    )
                )

        for tag in SOURCE_TAG_RE.findall(text):
            if tag.startswith(("nasa:", "scout:", "quoted:", "assumption:")) or tag == "computed":
                if tag not in self.allowed_sources:
                    issues.append(
                        Issue(
                            code="undeclared_source",
                            message="source tag is not declared by the result",
                            token=f"[{tag}]",
                        )
                    )

        return AuditResult(
            ok=not issues,
            issues=tuple(issues),
            numbers_checked=checked,
            sources=tuple(sorted(matched_sources)),
        )
