# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Build a short WhatsApp Field Card, a local QR and a printable HTML card."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

import segno

from .number_auditor import NumberAuditor
from .text import format_template, label, load_content
from .view import rotation_label, template_values, top_rotation

LIMIT = 590


@dataclass(frozen=True)
class FieldCard:
    site_id: str
    mode: str
    language: str
    whatsapp_text: str
    qr_svg: str
    print_html: str

    @property
    def length(self) -> int:
        return len(self.whatsapp_text)


def _fit(parts: list[tuple[str, str]], limit: int = LIMIT) -> str:
    """Drop optional lines before truncating, so the mode, range and caveat survive."""
    remaining = list(parts)
    for optional in ("blind", "scout", "water"):
        text = "\n".join(value for _, value in remaining)
        if len(text) <= limit:
            return text
        remaining = [(key, value) for key, value in remaining if key != optional]
    text = "\n".join(value for _, value in remaining)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _whatsapp_text(result: dict[str, Any], language: str) -> str:
    templates = load_content("result_templates")["fieldcard"][language]
    values = template_values(result, language)
    parts = [
        ("title", format_template(templates["title"], values)),
        ("top", format_template(templates["top"], values)),
        ("water", format_template(templates["water"], values)),
        ("worst", format_template(templates["worst"], values)),
    ]
    if result["fusion"].get("used"):
        parts.append(("scout", format_template(templates["scout"], values)))
    parts.append(("blind", format_template(templates["blind"], values)))
    parts.append(("note", format_template(templates["note"], values)))
    return _fit(parts)


def _print_html(result: dict[str, Any], language: str, qr_svg: str) -> str:
    rotation = top_rotation(result)
    values = template_values(result, language)
    direction = "rtl" if language == "ar" else "ltr"
    title = label("print", "title", language)
    rows = [
        (label("print", "site", language), result["site_id"]),
        (label("print", "mode", language), values["mode"]),
        (label("print", "rotation", language), rotation_label(result, rotation, language)),
        (
            label("print", "profit", language),
            f"{values['p10']} – {values['p90']} {values['currency']}/ha · "
            f"{label('print', 'median', language)} {values['median']} {values['currency']}/ha",
        ),
        (
            label("print", "water", language),
            f"{values['w10']} – {values['w90']} mm/yr",
        ),
        (
            label("print", "worst", language),
            f"{values['year']}: {values['profit']} {values['currency']}/ha",
        ),
    ]
    if result["fusion"].get("used"):
        rows.append(
            (
                label("print", "scout", language),
                f"{values['points']} · ESS {values['ess']} · {values['without']} → "
                f"{values['with']} {values['band_unit']}",
            )
        )
    rows_html = "\n".join(
        f"<tr><th>{escape(name)}</th><td>{escape(value)}</td></tr>" for name, value in rows
    )
    blindspots = load_content("blindspots")["blindspots"][:4]
    blind_html = "\n".join(
        "<li><strong>{}</strong> — {}</li>".format(
            escape(str(item["title_ar" if language == "ar" else "title_en"])),
            escape(str(item["review_action_ar" if language == "ar" else "review_action_en"])),
        )
        for item in blindspots
    )
    note = label("print", "note", language)
    qr_label = label("print", "qr", language)
    return f"""<!doctype html>
<html lang="{language}" dir="{direction}">
<head>
<meta charset="utf-8">
<title>{escape(title)} · {escape(str(result['site_id']))}</title>
<style>
  body {{ font: 15px/1.5 system-ui, sans-serif; color: #17211b; margin: 24px; }}
  main {{ max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 24px; margin: 0 0 4px; }}
  .mode {{ display: inline-block; border: 1px solid #17211b; border-radius: 999px;
           padding: 2px 10px; font-size: 12px; letter-spacing: .08em; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th, td {{ border-bottom: 1px solid #ccd5cf; padding: 7px 4px; text-align: start; }}
  th {{ width: 38%; font-weight: 600; }}
  ul {{ padding-inline-start: 20px; }}
  .qr {{ display: flex; gap: 14px; align-items: center; margin-top: 18px; }}
  .qr svg {{ width: 132px; height: 132px; }}
  .note {{ color: #4b5a51; font-size: 13px; margin-top: 18px; }}
  @media print {{ body {{ margin: 0; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
<main>
  <h1>{escape(title)}</h1>
  <span class="mode">{escape(values['mode'])}</span>
  <table>{rows_html}</table>
  <h2>{escape(label('print', 'blind', language))}</h2>
  <ul>{blind_html}</ul>
  <div class="qr">{qr_svg}<span>{escape(qr_label)}</span></div>
  <p class="note">{escape(note)} <code>[computed]</code></p>
</main>
</body>
</html>
"""


def make_field_card(result: dict[str, Any], language: str = "en") -> FieldCard:
    """Build a card whose WhatsApp text is audited and whose QR is generated locally."""
    if language not in {"en", "ar"}:
        raise ValueError(f"unsupported language: {language}")
    text = _whatsapp_text(result, language)
    audit = NumberAuditor(result).check(text)
    if not audit.ok:
        raise AssertionError(f"field card failed its own audit: {audit.reason}")
    qr = segno.make(text, error="m")
    qr_svg = qr.svg_inline(scale=4, border=2, dark="#17211b", light="#ffffff")
    return FieldCard(
        site_id=str(result["site_id"]),
        mode=str(result["mode"]),
        language=language,
        whatsapp_text=text,
        qr_svg=qr_svg,
        print_html=_print_html(result, language, qr_svg),
    )
