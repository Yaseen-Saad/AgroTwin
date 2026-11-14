# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""FastAPI service for AgroTwin.

The service serves contract-valid fixtures at Gate 1 and swaps in the replay engine behind the
same result schema when the Builder lands it. Every response carries ``mode`` and source tags.
"""

from __future__ import annotations

__all__: list[str] = []
