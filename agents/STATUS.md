# Status Snapshot

> Updated: 2026-11-14 · Gate: **0 passed; Gate 1 in progress** · Version: **0.1.0**
> Owner of this file: **Agent L**. The Builder reports through `MESSAGES.md`.

## One-line state

Gate 0 is tagged and green. Fixture API, bilingual web app, B-01 caches, B-02 replay and the
L-04 Council core are built. B-03 economics is active; Scout hardware samples and human visual
and native-Arabic review remain. Repo-wide ruff is waiting on two Builder lint fixes.

## Agents

| Agent | Current task | Status | Next |
| --- | --- | --- | --- |
| Lead (L) | `L-04` content, Council and Number Auditor | `REVIEW` | Human Arabic review; L-05 after B-02/B-03/B-04 |
| Builder (B) | `B-03` economics, barcode and ranking | `IN_PROGRESS` | B-04 fusion after acceptance |

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
| `python -m pytest` | 151 passed | 2026-11-14 |
| `python -m pytest tests/api` | 20 passed | 2026-11-14 |
| `python -m pytest tests/ingest` | 36 passed | 2026-11-14 |
| `python -m pytest tests/engine` | 28 passed | 2026-11-14 |
| `python -m pytest tests/econ` | 17 passed | 2026-11-14 |
| `python -m pytest tests/council` | 41 passed | 2026-11-14 |
| `python -m pytest` | 210 passed | 2026-11-14 |
| `python -m ruff check .` | 1 Builder-owned error remains (see MSG-0014) | 2026-11-14 |
| `npm --prefix web run build` | static `/` built, TypeScript clean | 2026-11-14 |
| Headless Chrome, 360 px | Arabic RTL + English LTR, no overflow, 0 console errors | 2026-11-14 |

## Known gaps

- `api/` serves contract-valid fixtures; the real-engine swap waits on B-02.
- `web/` is built and falls back to the bundled fixture when the API is offline. Visual
  greyscale and native Arabic review are still open human jobs.
- `/demo` still supports only `delta_01`; `matruh_01` and `sevilla_01` show `Cache pending`.
- `content/` and `council/` are built but not yet wired into the API or web; the `web/` Field
  Card remains its own client-side component until L-06 integration.
- Native Arabic review and the Field Card's human print check are still open.
- Repo-wide ruff has one remaining Builder-owned error: an unused import in
  `tests/econ/test_econ.py`.
- `qa/REPORT.md` does not exist yet; nothing may be presented as a validated result.
