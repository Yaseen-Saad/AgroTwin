# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The version must agree across VERSION, pyproject.toml and the package."""

from __future__ import annotations

import re
import tomllib

from agrotwin import REPO_ROOT, __version__, read_version


def test_version_file_matches_package() -> None:
    assert __version__ == read_version()
    assert __version__ == (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_pyproject_matches_version_file() -> None:
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    assert project["name"] == "agrotwin"
    assert project["version"] == __version__


def test_version_is_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
