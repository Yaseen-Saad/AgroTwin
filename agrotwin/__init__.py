# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""AgroTwin package metadata and repository helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"


def read_version() -> str:
    """Return the single-source repository version, falling back to package metadata."""
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        try:
            return distribution_version("agrotwin")
        except PackageNotFoundError:
            return "0.0.0"


__version__ = read_version()

__all__ = ["REPO_ROOT", "VERSION_FILE", "__version__", "read_version"]
