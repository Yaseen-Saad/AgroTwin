# Decision Log

Append-only. Every decision that changes ownership, contracts, data sources or scope goes here.
Format: id, date, decision, reason, consequences, owner.

---

## DEC-001 · Two-agent build mode

- **Date:** 2026-11-14
- **Decision:** Run the sprint with two agents: Agent L (Lead) and Agent B (Builder). Agent L
  absorbs the old roles 0, 5, 6, 7, 8, 10; Agent B absorbs 1, 2, 3, 4, 9.
- **Reason:** One builder on the computational core plus one lead on integration gives the
  fastest critical path without folder collisions.
- **Consequence:** The ten-role roster in `AGENTS.md` remains the reference for responsibilities,
  but execution is routed through this split.

## DEC-002 · Contracts are frozen at 1.0.0 for Gate 0

- **Date:** 2026-11-14
- **Decision:** No field rename or removal without a major bump. Additive optional fields need a
  minor bump, a fixture and a changelog entry.
- **Reason:** The Builder must implement against stable shapes; contract churn is the fastest way
  to lose a hackathon.
- **Consequence:** Builder requests go through `MESSAGES.md`; only the Lead edits `contracts/`.

## DEC-003 · One writer per path

- **Date:** 2026-11-14
- **Decision:** Lead and Builder never edit the same folder in the same wave. The ownership
  table in `agents/README.md` is binding.
- **Reason:** Shared files are the main failure mode of parallel agents.
- **Consequence:** Cross-folder needs are `CHANGE_REQUEST` messages, not edits.

## DEC-004 · Evidence-based done

- **Date:** 2026-11-14
- **Decision:** A task is `DONE` only after the Lead re-runs its acceptance command and merges.
- **Reason:** Agent reports are not evidence; commands are.
- **Consequence:** `MESSAGES.md` must contain the command and output for every task.

## DEC-005 · No commits or pushes by the Builder

- **Date:** 2026-11-14
- **Decision:** The Builder writes files in the shared tree; the Lead commits with Conventional
  Commits and tags releases.
- **Reason:** Two agents committing in one worktree risks lost work and unreviewable history.
- **Consequence:** The Lead reviews the diff and creates small commits.

## DEC-006 · Real data never blocks the demo

- **Date:** 2026-11-14
- **Decision:** Every network path is cache-first with a 3-second timeout and a fallback.
  If Earthdata fails, NDVI/SMAP fields are `null`; if the robot fails, use REPLAY or SIMULATED
  and show the badge.
- **Reason:** A live failure on stage is worse than a labelled fallback.
- **Consequence:** `NONE`, `REPLAY` and `SIMULATED` are first-class modes, not apologies.

## DEC-007 · No new scope after Gate 2

- **Date:** 2026-11-14
- **Decision:** After Gate 2, only fixes, content, Arabic review, QA and packaging. P1 work
  stops unless every P0 row is green and the Lead explicitly reopens it.
- **Reason:** The cut order in `SPEC.md` §9 exists to protect the submission.
- **Consequence:** Unfinished P1 items become mockups or are deleted from the pitch.
