# Status Snapshot

> Updated: 2026-11-14 · Gate: **0 passed** · Version: **0.1.0**
> Owner of this file: **Agent L**. The Builder reports through `MESSAGES.md`.

## One-line state

Contracts, fixtures, versioning and the assumptions ledger are written. Gate 0 acceptance
(validate, test, lint, tag) is in progress. Builder is assigned POWER ingest; Lead is finishing
the spine and the API on fixtures.

## Agents

| Agent | Current task | Status | Next |
| --- | --- | --- | --- |
| Lead (L) | `L-03` web app and lenses | `IN_PROGRESS` | L-02 real-engine swap after B-02 |
| Builder (B) | `B-01` POWER ingest and 3 caches | `ASSIGNED` | `B-02` water balance and replay |

## Gate checklist

| Gate 0 item | State |
| --- | --- |
| `SPEC.md` with P0 list and 3 demo sites | done |
| Five JSON Schemas + fixtures | done |
| `AGENTS.md` operating manual | done |
| `VERSION` 0.1.0 + `pyproject.toml` + `__version__` | done |
| Assumptions ledger + soil classes + provisional crops | done |
| `Makefile` + `tasks.ps1` + CI | done |
| Contract validation green | done — 7/7 fixtures valid |
| Pytest green | done — 67 passed |
| Ruff green | done — all checks passed |
| `HANDOFF.md` Gate 0 checkpoint | done |
| `docs/AI_USE.md` bootstrap entry | done |
| `gate-0` tag | done — `2a7986d`, tag `gate-0` |

## Environment

- Windows 11, PowerShell 5.1, Python 3.11.9, Node 24.
- `make` is absent; use `.\tasks.ps1` or `python -m ...`.
- Installed: `jsonschema`, `PyYAML`, `pytest`, `fastapi`, `uvicorn`, `httpx`, `ruff`.
- Live network reachable at time of setup; Earthdata credentials still missing.

## Blockers

| Blocker | Impact | Owner | Workaround |
| --- | --- | --- | --- |
| Earthdata/AppEEARS credentials not supplied | NDVI and SMAP fields ship `null` | Lead (human) | POWER-only caches; label the gap |
| Ali's serial log, photos, model metrics pending | Scout bridge and vision numbers blocked | Lead (human) | Simulator + REPLAY fixture; mark simulated |
| Soil-probe calibration pending | Fusion cannot run on real readings | Lead (human) | Refuse fusion without calibration id |
| Hub deadline and prior-work declaration unconfirmed | Submission risk | Lead (human) | Assume Sunday 20:00; confirm today |

## Last green commands

| Command | Result | When |
| --- | --- | --- |
| `python -m contracts.validate --all` | 7/7 fixtures valid | 2026-11-14 |
| `python -m pytest` | 87 passed | 2026-11-14 |
| `python -m pytest tests/api` | 20 passed | 2026-11-14 |
| `python -m ruff check .` | all checks passed | 2026-11-14 |

## Known gaps

- `api/` serves contract-valid fixtures; the real-engine swap waits on B-02.
- `web/` is empty; `L-03` starts against the fixture API.
- `content/` and `council/` are empty; `L-04` owns them.
- `qa/REPORT.md` does not exist yet; nothing may be presented as a validated result.
