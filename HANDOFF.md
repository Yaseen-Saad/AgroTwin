# Handoff and Gate Checkpoints

> Version: **0.1.0** · Current gate: **0 (bootstrap)** · Owner: **Agent L (Lead)**
> Live task board: `agents/TASKS.md` · Contact log: `agents/MESSAGES.md`

This file is the durable gate checkpoint and the record of human-only blockers. Day-to-day
cross-folder requests during the two-agent sprint belong in `agents/MESSAGES.md`; anything that
must survive a session or blocks a gate belongs here.

---

## Gate checkpoints

| Gate | When (Cairo) | State | Evidence |
| --- | --- | --- | --- |
| 0 | Sat 13:00 | **passed** | Commit `2a7986d`, tag `gate-0`; 7/7 fixtures, 67 tests, ruff clean |
| 1 | Sat 16:00 | **in progress** | Fixture API live (20 tests); web app and hardware samples pending |
| 2 | Sat 19:00 | not started | Real POWER caches; real engine behind the API |
| 3 | Sun 09:00 | not started | Feature freeze; Arabic review; first real QA report |
| 4 | Sun 14:00 | not started | Video, deck, project page, AI-use log |
| Submit | Sun 20:00 | not started | Submit what is green |

### Gate 0 checklist

- [x] `SPEC.md` with P0 scope and three demo sites
- [x] Five JSON Schemas and fixtures (`contracts/`)
- [x] `AGENTS.md` operating manual and two-agent mode
- [x] `VERSION` 0.1.0 mirrored in `pyproject.toml` and `agrotwin.__version__`
- [x] Assumptions ledger, soil classes, provisional crop catalogue
- [x] `Makefile`, `tasks.ps1`, CI workflow
- [x] `python -m contracts.validate --all` green — `7/7 fixtures valid`
- [x] `python -m pytest` green — `67 passed in 1.11s`
- [x] `python -m ruff check .` green — `All checks passed!`
- [x] `docs/AI_USE.md` bootstrap entry
- [x] `gate-0` tag and clean tree — commit `2a7986d`, annotated tag `gate-0`

### Gate 0 command evidence

```text
python -m contracts.validate --all
OK    site       site.delta_01.json
OK    rotation   rotation.existing.json
OK    rotation   rotation.alt_water.json
OK    rotation   rotation.alt_soil.json
OK    scout_run  scout_run.simulated.json
OK    replay     replay.delta_01.json
OK    result     result.delta_01.json

7/7 fixtures valid

python -m pytest
67 passed in 1.11s

python -m ruff check .
All checks passed!
```

---

## Human-only jobs

These cannot be delegated to an agent. The Lead owns every one and records the result here.

| # | Job | Owner | By (Cairo) | State |
| --- | --- | --- | --- | --- |
| 1 | Confirm the hub's real 2026 deadline and prior-work declaration rules for Verdex | Lead (human) | Today, before 13:00 | **open** |
| 2 | Confirm Ali is a registered team member at the same local event and consents to disclosure | Lead (human) | Today | **open** |
| 3 | Receive Ali's sample serial log, photos with permission, dataset size, held-out accuracy and confusion matrix | Lead + Ali | Sat 13:00 | **open** |
| 4 | Create an Earthdata login for AppEEARS and expose it as environment variables only | Lead (human) | Sat 13:00 | **blocked**; POWER-only fallback in use |
| 5 | Flash the ESP32 sketch or run the laptop bridge so readings reach `/scout/run` | Ali | Sat 18:00 | **open** |
| 6 | Calibrate the soil probe on demo-plot soil (weigh, oven-dry, reweigh) | Ali | Sat 18:00 | **open** |
| 7 | Record one LIVE run and one saved REPLAY run with a drying day | Ali | Sat 23:00 | **open** |
| 8 | Spend 15 minutes with a farmer or agronomist reviewing the crop table and Farmer lens wording | Lead (human) | Sun 09:00 | **open** |
| 9 | Native Arabic review of `web/i18n/ar.json` and `content/` | Lead (human) | Before Gate 3 | **open** |
| 10 | Rehearse twice and record the 30-second video with English subtitles | Lead (human) | Sun 14:00 | **open** |
| 11 | Check every form field and submit for judging | Lead (human) | Sun 20:00 | **open** |

If the robot is not posting by Gate 2, the demo uses a REPLAY of earlier real logs or a
SIMULATED run, with the badge visible and a spoken disclosure. Never pretend a simulated run is
live.

---

## Agent L (Lead) — current handoff

**Done this session**

- Repository skeleton, `SPEC.md`, `AGENTS.md`, `HANDOFF.md`, versioning, Makefile and Windows
  task runner.
- Five frozen JSON Schemas + valid fixtures + `contracts/validate.py` with cross-field checks.
- Assumption ledger, soil-class table, provisional crop catalogue, ET0 and units modules.
- `agrotwin` package with a single-source `__version__`.
- Two-agent coordination room in `agents/`.

**Next**

1. L-03: web app and three lenses on the fixture API.
2. L-02 remainder: swap the real engine behind the unchanged result schema when B-02 lands.
3. L-04: content, Council and the Number Auditor.

**L-02 fixture evidence**

```text
python -m pytest tests/api      -> 20 passed
python -m pytest               -> 87 passed
python -m contracts.validate   -> 7/7 fixtures valid
python -m ruff check .         -> all checks passed
```

Endpoints: `GET /health`, `GET /demo/{site}`, `GET /demo/{site}/feddan`, `POST /diagnose`,
`POST /simulate`, `POST /scout/run`, `POST /scout/calibrate`, `POST /fieldcard`. Scout intake
rejects a bad token before parsing the body and refuses a calibrated reading without a
calibration id. All fixture results keep `mode` and add an illustrative-fixture note.

**Blockers**

- Earthdata credentials missing → NDVI/SMAP fields stay `null` until supplied.
- Real Scout data missing → simulator and REPLAY only; fusion refuses without a calibration id.
- Hub deadline unconfirmed → plan assumes Sunday 20:00 with a compressed fallback.

---

## Agent B (Builder) — current handoff

**Assigned:** `B-01` POWER ingest and three site caches. See `agents/TASKS.md` and MSG-0001.

**Owned paths:** `ingest/`, `engine/`, `data/cache/`, `data/prices.csv`, `scout/`, and matching
tests. **Never edits:** contracts, API, web, content, council, QA, docs, the board.

**First checkpoint:** post evidence in `agents/MESSAGES.md` within 45 minutes, then fast-lane to
`B-02` if B-01 acceptance passes.

---

## Cross-folder requests

No open `CHANGE_REQUEST` at Gate 0.

Use this template in `agents/MESSAGES.md`:

```markdown
### MSG-000N · <from> → <to> · <date time> · <task> · CHANGE_REQUEST
Need:      <one sentence>
Why:       <contract or demo reason>
Requested: <exact field, file or diff>
Fallback:  <what is happening meanwhile>
```

---

## Known weaknesses (carry into the pitch)

These are honest limitations, not bugs to hide:

1. `engine/crops.yaml` coefficients and Egyptian planting windows are **provisional** until Agent
   B verifies FAO-56/FAO-33 rows and an agronomist reviews them.
2. `data/prices.csv` will be assumption-tagged until a real Egyptian farmgate source is confirmed.
3. SMAP and MODIS are not cached yet; the hindcast and bias check may print `not run`.
4. The Verdex vision metrics are unconfirmed; only Ali's own held-out numbers may be quoted.
5. The template, barcode and fusion blocks in the result fixture are illustrative; they must be
   replaced by engine outputs before any claim is made.
6. Power data is historical; the product does not forecast rainfall.
7. The MVP has no carbon-credit claim and no live WhatsApp bot.
