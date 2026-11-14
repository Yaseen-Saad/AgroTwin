# AGENTS.md — Operating Manual for AgroTwin Contributors

This file is the contract for every human and AI agent working in this repository. Read it fully
before writing code. `SPEC.md` defines **what** to build; this file defines **how** to work
without breaking another agent's work.

> Repository version: **0.1.0** · Gate: **0 (bootstrap)** · Owner of merges: **Agent 0 (Lead)**

---

## 1. Read order

1. `SPEC.md` — product scope, P0 list, demo sites, units, criteria.
2. `contracts/README.md` — the frozen interfaces.
3. `contracts/*.schema.json` — the actual shapes.
4. `contracts/fixtures/` — valid examples. These are the only data you may rely on at Gate 0.
5. `engine/config/assumptions.yaml` — every editable threshold and its tag.
6. `HANDOFF.md` — open blockers and cross-folder requests.
7. `docs/AI_USE.md` — AI disclosure log you must append to.

---

## 2. Prime directives

1. **Contracts first.** Code against `contracts/`, never against another agent's implementation.
2. **One owner per folder.** Never edit files outside your folder. Request changes in
   `HANDOFF.md`.
3. **Every number carries a source tag.** `nasa:<product>`, `computed`, `scout:<run_id>`,
   `quoted:<url>` or `assumption:<tag>`. No exceptions, including UI mockups.
4. **Ranges, not promises.** Never render a single-point outcome where an ensemble exists.
5. **Honest modes.** `LIVE`, `REPLAY`, `SIMULATED`, `NONE` travel with the data end to end and
   are always visible.
6. **No invented facts.** If a coefficient, price or citation cannot be sourced, tag it
   `assumption:<name>`, make it editable, and list it as a known weakness.
7. **Cut, don't extend.** Anything not green at a gate is cut. No scope creep.
8. **Disclose AI.** Header comment in every code file, `generated_by` in every data file, entry
   in `docs/AI_USE.md`, and the submission's AI-use field.
9. **No NASA logos, flags or mission insignia.** Text references to NASA datasets are fine.
10. **Small commits.** One logical change per commit, on your own branch.

---

## 3. Ownership map

| Agent | Owns | May read | Never edits |
| --- | --- | --- | --- |
| 0 Lead | `SPEC.md`, `AGENTS.md`, `HANDOFF.md`, `contracts/`, `Makefile`, `tasks.ps1`, merges | everything | agent folders without a handoff |
| 1 Data ingest | `ingest/`, `data/cache/` | contracts, engine readers | `engine/` |
| 2 Replay engine | `engine/et0.py`, `waterbalance.py`, `replay.py`, `danger.py`, `crops.py`, `crops.yaml`, `config/` | contracts, ingest outputs | `engine/econ.py`, `engine/rank.py` |
| 3 Economics and ranking | `engine/econ.py`, `engine/rank.py`, `data/prices.csv` | replay outputs | `engine/replay.py` |
| 4 Fusion and checks | `engine/fusion.py`, `engine/biascheck.py`, `engine/twin.py` | replay, scout runs | `engine/replay.py` |
| 5 API and intake | `api/` | engine, contracts | engine, web |
| 6 Frontend and lenses | `web/` | API, fixtures, content | everything else |
| 7 QA and red team | `qa/` | everything | everything (read-only) |
| 8 Pitch and docs | `docs/` | everything | code |
| 9 Scout bridge | `scout/` | contracts, cache | firmware outside `scout/` |
| 10 Council and content | `council/`, `content/` | result contract | UI components |

Cross-folder need → write an entry in `HANDOFF.md` under the target agent's section. Do not edit
their files.

---

## 4. Contract discipline

The five contracts are frozen at Gate 0:

| File | Purpose | Version |
| --- | --- | --- |
| `contracts/site.schema.json` | Cached field site with POWER daily rows | 1.0.0 |
| `contracts/rotation.schema.json` | Three-year crop rotation request | 1.0.0 |
| `contracts/scout_run.schema.json` | Verdex sensor run (LIVE/REPLAY/SIMULATED) | 1.0.0 |
| `contracts/replay.schema.json` | Agronomic engine output per historical window | 1.0.0 |
| `contracts/result.schema.json` | Full API/UI result, including barcode and fusion | 1.0.0 |

Rules:

- Validate locally with `python -m contracts.validate --all` before every commit that touches
  data or schemas.
- Additive, optional fields require a minor schema version bump and a fixture update.
- Renames, removals or type changes require a major bump, a migration note and lead approval.
- Never "fix" data to fit a schema without recording why in `CHANGELOG.md`.
- If a schema is wrong, propose the change in `HANDOFF.md`; do not silently fork it.

### Units

- Engine: hectares, millimetres, EGP, UTC timestamps.
- API: per-hectare values plus per-feddan values. `1 feddan = 0.42 ha`.
- Never mix hectares and feddans in one field. The unit is part of the contract.

---

## 5. Provenance and honesty rules

### Source tags

Exactly one tag per number:

```text
nasa:POWER            nasa:MODIS            nasa:SMAP
computed              scout:<run_id>        quoted:<url>
assumption:<name>
```

Assumption names must exist in `engine/config/assumptions.yaml`. Add a new assumption there
before using its tag.

### Modes

| Mode | Meaning | Allowed in demo |
| --- | --- | --- |
| `LIVE` | Robot is posting now | Yes, with badge |
| `REPLAY` | Saved real run, played back | Yes, with badge |
| `SIMULATED` | Generated readings (twin experiment or fallback) | Yes, with badge and spoken disclosure |
| `NONE` | No scout data used | Yes |

Mode is mandatory. `api/` must reject a Scout run without it.

### Forbidden claims

Never write, render or say:

- "will", "guaranteed", "certain" about an outcome, in any language.
- A rainfall forecast derived from POWER.
- A specific yield, water-saving or revenue claim not produced by the engine.
- A vision accuracy number other than the author's own held-out metric.
- A carbon-credit dollar figure.
- Field-level aquifer health from GRACE-FO.

---

## 6. Versioning policy

Single source of truth: `VERSION` (currently `0.1.0`). It is mirrored in `pyproject.toml` and
exposed as `agrotwin.__version__` and `GET /health.version`.

- **MAJOR** — breaking contract change, schema removal, data model rewrite.
- **MINOR** — new capability, additive schema field, new endpoint.
- **PATCH** — fixes, docs, coefficients with citations, test-only changes.

Rules:

1. Bump `VERSION`, `pyproject.toml` and `CHANGELOG.md` in the same commit.
2. Tag releases `vX.Y.Z`; tag gates `gate-N`.
3. Never edit a released tag. Ship a new patch.
4. Test that `VERSION`, `pyproject.toml` and `agrotwin.__version__` agree
   (`tests/test_version.py`).
5. Schema versions are independent and live in each schema as `"x-schema-version"`.

---

## 7. Git workflow

- Work in a branch or worktree: `agent-<N>-<topic>`.
- Commit style: Conventional Commits — `feat(engine): add FAO-56 ET0`,
  `fix(api): reject scout run without mode`, `docs(spec): ...`, `test(qa): ...`.
- Never commit `.env`, credentials, `scout/esp32/config.h`, build output or large raw data.
- Only the lead merges to `main`, at gates or every two hours.
- If `main` is red for 20 minutes, all work stops until it is green.
- Merge checklist: `python -m contracts.validate --all` · `python -m pytest` ·
  `python -m ruff check .` · status checkpoint in `HANDOFF.md`.

---

## 8. Definition of done

An agent is done only when **the lead can run the command**:

| Agent | Command | Pass condition |
| --- | --- | --- |
| 1 | `python -m pytest tests/ingest` + `python -m contracts.validate --all` | 3 caches valid, fallback test passes |
| 2 | `python -m pytest tests/engine` | Golden case, mass balance, fallow, reproducibility, <2 s |
| 3 | `python -m pytest tests/econ` | Profit/price monotonicity, legume credit, exclusion |
| 4 | `python -m pytest tests/fusion` + `python -m engine.twin` | Coverage and width reported, ESS guard holds |
| 5 | `python -m pytest tests/api` | Schema-valid, <3 s, bad token rejected, demo route works |
| 6 | `npm --prefix web run build` + manual checklist | All lenses, RTL, badges, source chips, 360 px |
| 7 | `python -m qa.validation_wall` | `qa/REPORT.md` filled with real results or `not run` |
| 8 | Manual doc audit | All required docs and submission fields complete |
| 9 | `python -m pytest tests/scout` | Every generated run schema-valid; calibrate rejects <3 samples |
| 10 | `python -m pytest tests/council` | 10 bad claims blocked, 10 good passed; WhatsApp <600 chars |

A report without a green command is not done.

---

## 9. Gates and cut order

| Gate | When (Cairo) | Condition |
| --- | --- | --- |
| 0 | Sat 13:00 | Spec, schemas, fixtures, Makefile, sites committed; tests green |
| 1 | Sat 16:00 | End-to-end on fixtures; simulator narrows the band; hardware samples received |
| 2 | Sat 19:00 | Real POWER data, real engine behind API, barcode on real data |
| 3 | Sun 09:00 | Feature freeze; reviewed Arabic; Council + auditor; first QA report |
| 4 | Sun 14:00 | Video with English subtitles; deck; project page; AI_USE complete |
| Submit | Sun 20:00 | All fields checked; submit what is green |

Cut order when time runs short: live WhatsApp bot → Open-Meteo weighting → sub-field zones and
co-op → agronomist handoff page → plain-English toggle → SMAP comparison slide. Never cut the
P0 rows in `SPEC.md` §3.

---

## 10. Commands (Windows-aware)

GNU `make` is optional on this workstation. Both interfaces are first-class:

```powershell
.\tasks.ps1 validate     # contract validation
.\tasks.ps1 test         # pytest
.\tasks.ps1 lint         # ruff
.\tasks.ps1 api          # FastAPI on 127.0.0.1:8000
.\tasks.ps1 web          # Next.js (npm install in web/ first)
.\tasks.ps1 version
```

```bash
make validate
make test
make lint
make api
make web
make version
```

CI runs validate, test and lint on every push (`.github/workflows/ci.yml`).

---

## 11. AI disclosure (mandatory)

The submission requires stating where and how AI was used.

For every generated code file, add this header immediately after any shebang:

```python
# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
```

Use `//` for `.ino`, `/* ... */` for CSS, `<!-- -->` for HTML/Markdown where appropriate.

For every generated data file (JSON, CSV, YAML), add a field or leading row:

```json
"generated_by": "agent-2 / <tool> / 2026-11-14"
```

Then append a row to `docs/AI_USE.md`: date, agent, tool, files, what was generated, human
reviewer. Never claim a human reviewed something that was not reviewed.

---

## 12. Security and privacy

- Secrets come from environment variables only. Never commit `.env`, tokens, Earthdata
  credentials or Wi-Fi passwords.
- `scout/esp32/config.h` is git-ignored; commit only `config.example.h`.
- Validate and range-check every ingested Scout run; reject bad tokens before parsing the body.
- Farmer data stays local and exportable. No third-party analytics in the MVP.
- Do not log full request bodies or coordinates in production logs.
- Report a suspected secret leak to the lead immediately; rotate the secret.

---

## 13. Code and data conventions

Crystallised rules for this repo:

- Python 3.11. Type hints on public functions. Docstrings explain units and contract references.
  No `print` in library code; the CLI may print JSON.
- Imports: stdlib, third-party, local. `ruff check` must pass.
- All paths resolve from the repository root via `pathlib.Path(__file__)`, never the process CWD.
- JSON is UTF-8, two-space indent, trailing newline, keys in schema order.
- Timestamps are ISO-8601 UTC with `Z` or `+00:00`.
- Arabic text lives only in `web/i18n/ar.json` and `content/`; components never hard-code copy.
- Charts and barcodes must remain readable in greyscale and at 360 px width.
- Name files `snake_case.py`, `kebab-case.tsx`, `site_id.json`, `YYYY-MM-DD` in prose.

---

## 14. Escalation and handoff

- Blocked more than 30 minutes → write the blocker in `HANDOFF.md`, continue with mocks, tell the
  lead.
- Cross-folder change → `HANDOFF.md` entry with the exact requested diff or field.
- Agent stalled >30 minutes → lead reassigns or cuts the feature.
- Every gate → each agent posts pass/fail per item in `HANDOFF.md` with the command output.

`HANDOFF.md` entry template:

```markdown
### Agent N → Agent M · 2026-11-14 14:05
Need: <one sentence>
Why: <contract or demo reason>
Requested change: <exact field/file>
Fallback in use: <what I am doing meanwhile>
```

---

## 15. Environment notes

- OS: Windows 11, PowerShell 5.1. `make` is not installed; use `.\tasks.ps1`.
- Python 3.11.9. Node 24. Create the Next.js app under `web/`.
- Repository root is the workspace root; never assume the CWD.
- Keep paths inside the repo; use the system temp dir for scratch work.
- If `jsonschema` or `PyYAML` is missing: `.\tasks.ps1 install`.

---

## 16. Agent roster (one-line briefs)

| # | Agent | Folder | One-line mission |
| --- | --- | --- | --- |
| 0 | Lead | root/contracts | Own spec, contracts, versioning and every merge |
| 1 | Data ingest | `ingest/`, `data/cache/` | POWER daily caches for 3 sites, optional AppEEARS, 3 s fallback |
| 2 | Replay engine | `engine/` (agronomy) | FAO-56 ET0 + daily water balance + replay + danger windows |
| 3 | Economics & ranking | `engine/econ.py`, `rank.py`, `data/prices.csv` | Profit ranges, barcode class, weighted ranking, constraints |
| 4 | Fusion & checks | `engine/fusion.py`, `biascheck.py`, `twin.py` | Weighted analog ensemble, ESS guard, twin coverage |
| 5 | API & intake | `api/` | FastAPI endpoints, Scout intake, caching, precomputed demo |
| 6 | Frontend & lenses | `web/` | Map, barcode, mixer, sliders, 3 lenses, RTL, source chips |
| 7 | QA & red team | `qa/` | Validation wall, provenance audit, hostile-judge weakness list |
| 8 | Pitch & docs | `docs/` | Methods, sources, AI use, unit economics, deck, video script |
| 9 | Scout bridge | `scout/` | ESP32 sketch, bridge, simulator, replay, calibration |
| 10 | Council & content | `council/`, `content/` | Advisors + Number Auditor, glossary, blind spots, Field Card |

Detailed prompts are in the planning document (Agent guide §6). When a prompt and this file
conflict, this file and `SPEC.md` win; raise the conflict in `HANDOFF.md`.

---

## 17. Two-agent build mode (this sprint)

The 2026-11-14 sprint runs with two agents. `agents/` is the live coordination surface; this
section only changes **who executes**, never the rules in §§2-15.

| Agent | Absorbs old roles | Writes | Never edits |
| --- | --- | --- | --- |
| **Agent L (Lead)** | 0, 5, 6, 7, 8, 10 | root docs, `contracts/`, `api/`, `web/`, `content/`, `council/`, `qa/`, `docs/`, `agents/TASKS.md`, `agents/STATUS.md` | `ingest/`, `engine/`, `data/`, `scout/` without a task |
| **Agent B (Builder)** | 1, 2, 3, 4, 9 | `ingest/`, `engine/`, `data/cache/`, `data/prices.csv`, `scout/`, matching `tests/` | contracts, `api/`, `web/`, `content/`, `council/`, `qa/`, `docs/`, the board |

Binding rules for the sprint:

1. `agents/README.md` is the protocol; `agents/TASKS.md` is the single task board.
2. `agents/MESSAGES.md` is the append-only contact log. A task is not done until the Lead
   re-runs its acceptance command and merges.
3. The Builder does not commit or push. The Lead is the only merge owner and the only agent that
   changes `contracts/`, `VERSION` or `pyproject.toml`.
4. One `IN_PROGRESS` task per agent. Cross-folder needs are `CHANGE_REQUEST` messages, not edits.
5. `HANDOFF.md` remains the gate checkpoint and human-blocker record.
6. When this section conflicts with an agent prompt, `SPEC.md`, this file and the frozen
   contracts win. Raise the conflict in `agents/MESSAGES.md` immediately.
