# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
"""The two-agent coordination surface stays consistent and append-only."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"

REQUIRED_FILES = (
    "README.md",
    "CHARTER.md",
    "TASKS.md",
    "MESSAGES.md",
    "STATUS.md",
    "DECISIONS.md",
    "prompts/builder-bootstrap.md",
)

BOARD_TASKS = (
    "L-01",
    "L-02",
    "L-03",
    "L-04",
    "L-05",
    "L-06",
    "L-07",
    "B-01",
    "B-02",
    "B-03",
    "B-04",
    "B-05",
    "B-06",
)


def _read(name: str) -> str:
    return (AGENTS / name).read_text(encoding="utf-8")


def test_coordination_files_exist() -> None:
    for name in REQUIRED_FILES:
        path = AGENTS / name
        assert path.is_file(), name
        assert path.read_text(encoding="utf-8").strip(), name


def test_board_has_every_task_card() -> None:
    board = _read("TASKS.md")
    for task in BOARD_TASKS:
        assert board.count(task) >= 2, f"{task} needs a board row and a card"
    assert re.search(r"^\| L-01 \| L \| 0 \| P0 \|", board, re.MULTILINE)
    assert re.search(r"^\| B-01 \| B \| 0 \| P0 \|", board, re.MULTILINE)


def test_one_active_task_per_agent() -> None:
    board = _read("TASKS.md")
    assert board.count("`IN_PROGRESS`") >= 1
    lead_block = board.split("### L-03", 1)[1].split("### L-04", 1)[0]
    builder_block = board.split("### B-01", 1)[1].split("### B-02", 1)[0]
    assert "**Status:** `IN_PROGRESS`" in lead_block
    assert "**Status:** `ASSIGNED`" in builder_block


def test_messages_are_append_only_and_well_formed() -> None:
    messages = _read("MESSAGES.md")
    headers = re.findall(r"^### (MSG-\d{4}) · .+$", messages, re.MULTILINE)
    assert len(headers) >= 5
    assert headers == sorted(headers), "message ids must increase"
    assert len(headers) == len(set(headers)), "message ids must be unique"

    blocks = re.split(r"^### MSG-\d{4} · ", messages, flags=re.MULTILINE)[1:]
    for block in blocks:
        for field in ("Task:", "Status:", "Body:", "Evidence:", "Needed by:"):
            assert field in block, f"message missing {field}"


def test_first_message_assigns_the_builder() -> None:
    messages = _read("MESSAGES.md")
    first = re.split(r"^### ", messages, maxsplit=2, flags=re.MULTILINE)[1]
    assert first.startswith("MSG-0001")
    assert "B-01" in first
    assert "ASSIGNED" in first


def test_status_names_both_agents_and_current_tasks() -> None:
    status = _read("STATUS.md")
    assert "Lead (L)" in status
    assert "Builder (B)" in status
    assert "`L-03`" in status
    assert "`B-01`" in status


def test_bootstrap_prompt_is_executable() -> None:
    prompt = _read("prompts/builder-bootstrap.md")
    assert "Agent B (Builder)" in prompt
    for required in (
        "agents/README.md",
        "agents/TASKS.md",
        "agents/MESSAGES.md",
        "SPEC.md",
        "AGENTS.md",
        "contracts/",
        "B-01",
        "B-02",
        "python -m pytest tests/ingest",
        "python -m contracts.validate --all",
    ):
        assert required in prompt, required
    assert "do not commit" in prompt.lower()
    assert "never edit contracts" in prompt.lower()


def test_disclosure_log_covers_the_bootstrap() -> None:
    disclosure = (ROOT / "docs" / "AI_USE.md").read_text(encoding="utf-8")
    assert "Agent L (Lead)" in disclosure
    assert "HANDOFF.md" in disclosure
    assert "human review" in disclosure
