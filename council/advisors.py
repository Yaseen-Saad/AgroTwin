# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Three constrained Council advisors with a fixed-template fallback."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .number_auditor import AuditResult, NumberAuditor
from .text import format_template, label, load_content
from .view import template_values, top_rotation

ADVISOR_IDS = ("agronomist", "economist", "scientist")
LENSES = ("farmer", "investor", "scientist")
LANGUAGES = ("en", "ar")
Provider = Callable[[str], str]


@dataclass(frozen=True)
class AdvisorReply:
    advisor_id: str
    advisor_name: str
    language: str
    lens: str
    text: str
    source: str
    audit: AuditResult
    fallback_reason: str | None = None


def _provider_prompt(
    result: dict[str, Any],
    advisor_id: str,
    lens: str,
    language: str,
) -> str:
    rotation = top_rotation(result)
    profit = rotation["metrics"]["profit_per_ha"]
    water = rotation["metrics"]["water_use_mm"]
    fusion = result["fusion"]
    facts = [
        f"site_id={result['site_id']}",
        f"mode={result['mode']}",
        f"replayed_years={len(result.get('years', []))}",
        f"top_rotation={rotation['rotation_id']}",
        f"profit_p10={profit['p10']}",
        f"profit_median={profit['median']}",
        f"profit_p90={profit['p90']}",
        f"currency={profit.get('currency', 'EGP')}",
        f"water_p10={water['p10']}",
        f"water_p90={water['p90']}",
        f"fusion_used={fusion.get('used')}",
        f"ess={fusion.get('ess')}",
        f"band_without={fusion['range_width']['without_scout']}",
        f"band_with={fusion['range_width']['with_scout']}",
    ]
    language_name = "Arabic" if language == "ar" else "English"
    return (
        "You are one advisor in AgroTwin's Council. Restate only the facts below. "
        "Do not add any number that is not listed. Do not promise, forecast, or claim yield, "
        "revenue, water saving or carbon credit. Do not diagnose a field or aquifer. "
        f"Advisor role: {label('advisor', advisor_id, 'en')}. Lens: {lens}. "
        f"Answer in {language_name}, in at most two sentences.\n"
        + "\n".join(f"- {fact}" for fact in facts)
    )


def _template_text(result: dict[str, Any], advisor_id: str, lens: str, language: str) -> str:
    templates = load_content("result_templates")
    values = template_values(result, language)
    template_key = advisor_id
    if advisor_id == "scientist" and not result["fusion"].get("used"):
        template_key = "scientist_no_scout"
    body = templates["advisors"][template_key][language]
    opening = templates["lens_openings"][lens][language]
    return f"{opening} {format_template(body, values)}"


def ask_council(
    result: dict[str, Any],
    language: str = "en",
    lens: str = "farmer",
    provider: Provider | None = None,
) -> tuple[AdvisorReply, ...]:
    """Return all three advisor replies; any provider or audit failure uses the template."""
    if language not in LANGUAGES:
        raise ValueError(f"unsupported language: {language}")
    if lens not in LENSES:
        raise ValueError(f"unsupported lens: {lens}")

    auditor = NumberAuditor(result)
    replies: list[AdvisorReply] = []
    for advisor_id in ADVISOR_IDS:
        name = label("advisor", advisor_id, language)
        template_text = _template_text(result, advisor_id, lens, language)
        fallback_audit = auditor.check(template_text)
        if not fallback_audit.ok:
            raise AssertionError(
                f"fixed template failed its own audit for {advisor_id}: {fallback_audit.reason}"
            )

        source = "template"
        text = template_text
        audit = fallback_audit
        fallback_reason: str | None = None
        if provider is not None:
            try:
                candidate = provider(_provider_prompt(result, advisor_id, lens, language))
            except Exception:
                fallback_reason = "provider_error"
            else:
                if not isinstance(candidate, str) or not candidate.strip():
                    fallback_reason = "provider_empty"
                else:
                    candidate_audit = auditor.check(candidate.strip())
                    if candidate_audit.ok:
                        text = candidate.strip()
                        audit = candidate_audit
                        source = "provider"
                    else:
                        fallback_reason = f"audit:{candidate_audit.reason}"

        replies.append(
            AdvisorReply(
                advisor_id=advisor_id,
                advisor_name=name,
                language=language,
                lens=lens,
                text=text,
                source=source,
                audit=audit,
                fallback_reason=fallback_reason,
            )
        )
    return tuple(replies)
