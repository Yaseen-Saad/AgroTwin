# Contact Log (append-only)

New messages go at the **end**. Never rewrite history. `STATUS.md` holds the current snapshot.
Message ids increase monotonically. Times are Cairo (UTC+2) unless stated.

---

### MSG-0001 · Lead → Builder · 2026-11-14 12:10 Cairo · B-01 · ASSIGNED

Task:      B-01 POWER ingest and three site caches
Status:    ASSIGNED
Body:      Read `agents/README.md`, `agents/CHARTER.md`, `agents/TASKS.md`, `SPEC.md`,
           `AGENTS.md` and all five schemas plus fixtures before writing code. Then implement
           `ingest/power.py`, `ingest/build_cache.py`, `ingest/serve.py`, the optional
           `ingest/appeears.py`, and `tests/ingest/`. Produce caches for `delta_01`, `matruh_01`
           and `sevilla_01` (coordinates in `SPEC.md` §5). Parameter names must come from the
           POWER catalogue, not memory. Do not edit contracts, `api/`, `web/`, `content/`,
           `council/`, `qa/`, `docs/` or this board.
Evidence:  none yet
Needed by: first checkpoint in 45 minutes

---

### MSG-0002 · Lead → Builder · 2026-11-14 12:12 Cairo · B-01 · CONTEXT

Task:      B-01
Status:    ASSIGNED
Body:      Current state: version 0.1.0; five schemas and fixtures exist; ET0, units, crop
           loader, assumptions ledger and soil-class table exist. `ingest/`, `engine/` stubs and
           `data/cache/` are yours. Python 3.11 with jsonschema, PyYAML, pytest, fastapi, httpx
           and ruff installed. `make` is absent; use `python -m ...`. Network access exists but
           must never block the demo: cache-first, 3-second live timeout, fallback.
Evidence:  `python -m contracts.validate --all` is the contract gate.
Needed by: no deadline

---

### MSG-0003 · Lead → Builder · 2026-11-14 12:14 Cairo · B-02 · PRE-ASSIGNED

Task:      B-02 Water balance, replay and danger windows
Status:    TODO (fast lane)
Body:      As soon as B-01 evidence is posted and its acceptance command passes, claim B-02
           without waiting for review. Implement to Agent guide §5.1, §5.2, §5.6 using
           `engine/et0.py`, `engine/crops.yaml` and `engine/config/soil_classes.yaml`. Verify
           every coefficient against FAO-56/FAO-33 and record the exact table; if a value cannot
           be verified, stop and send a `CHANGE_REQUEST` with an `assumption:<id>` proposal.
           Golden test arithmetic must be written in the test, not copied from the implementation.
Evidence:  none yet
Needed by: Gate 1-2

---

### MSG-0004 · Lead → Builder · 2026-11-14 12:16 Cairo · REPORT FORMAT

Task:      all
Status:    standing
Body:      Evidence message format: task id, status, files changed, exact commands run, pass/fail,
           what is mocked, what is missing, next task. Do not commit, push, switch branches or
           touch Lead-owned paths. If blocked >30 minutes, post `BLOCKED`, state the exact error,
           and start the next non-overlapping task. A cross-folder need is a `CHANGE_REQUEST`,
           not an edit.
Evidence:  command output pasted verbatim, trimmed to the relevant lines.
Needed by: every checkpoint

---

### MSG-0005 · Builder → Lead · 2026-11-14 — · B-01 · IN_PROGRESS

Task:      B-01
Status:    IN_PROGRESS
Body:      (Builder: replace this placeholder with your claim, first files, and any immediate
           blocker.)
Evidence:  none yet
Needed by: next checkpoint

---

<!-- Append new messages below this line. -->

---

### MSG-0006 · Lead → Builder · 2026-11-14 · B-01 · STATUS

Task:      B-01
Status:    ASSIGNED
Body:      Gate 0 is locally green: 7/7 fixtures valid, 67 tests pass, ruff clean. Contracts are
           frozen at 1.0.0 and no change request is open. B-01 remains your only active task; use
           the exact parameter names from the POWER catalogue and ship caches that validate.
Evidence:  `python -m contracts.validate --all` → 7/7; `python -m pytest` → 67 passed;
           `python -m ruff check .` → all checks passed.
Needed by: first B-01 checkpoint in 45 minutes

---

### MSG-0007 · Lead → Builder · 2026-11-14 · GATE-0 · STATUS

Task:      B-01
Status:    ASSIGNED
Body:      Gate 0 passed and is tagged `gate-0` at commit `2a7986d`. The contracts are now
           frozen for implementation; no schema edits will be made without a change request.
           Lead is starting L-02 (API on fixtures) in parallel with your POWER ingest.
Evidence:  `python -m contracts.validate --all` → 7/7; `python -m pytest` → 67 passed;
           `python -m ruff check .` → all checks passed; `git tag -n` → gate-0.
Needed by: no deadline


