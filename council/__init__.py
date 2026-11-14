# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""Constrained advisors, the Number Auditor and the printable Field Card."""

from __future__ import annotations

from .advisors import ADVISOR_IDS, LENSES, AdvisorReply, ask_council
from .field_card import FieldCard, make_field_card
from .number_auditor import AuditResult, Issue, NumberAuditor
from .text import load_content

__all__ = [
    "ADVISOR_IDS",
    "LENSES",
    "AdvisorReply",
    "AuditResult",
    "FieldCard",
    "Issue",
    "NumberAuditor",
    "ask_council",
    "load_content",
    "make_field_card",
]
