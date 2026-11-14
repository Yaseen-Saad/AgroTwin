# Handoff and Gate Checkpoints

> Version: **0.1.0** · Current gate: **1 (fixtures + web + Council core, engine review)** · Owner: **Agent L (Lead)**
> Live task board: `agents/TASKS.md` · Contact log: `agents/MESSAGES.md`

This file is the durable gate checkpoint and the record of human-only blockers. Day-to-day
cross-folder requests during the two-agent sprint belong in `agents/MESSAGES.md`; anything that
must survive a session or blocks a gate belongs here.

---

## Gate checkpoints

| Gate | When (Cairo) | State | Evidence |
| --- | --- | --- | --- |
| 0 | Sat 13:00 | **passed** | Commit `2a7986d`, tag `gate-0`; 7/7 fixtures, 67 tests, ruff clean |
| 1 | Sat 16:00 | **in progress** | 210 tests green; fixture API, web build, B-01 caches and L-04 Council core done; hardware samples pending |
| 2 | Sat 19:00 | **in progress** | POWER caches ready; B-02 replay in REVIEW; real-engine API swap and B-03/B-04 still open |
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
- Fixture-backed FastAPI service with Scout intake, calibration and field card.
- Bilingual Next.js 16 web app: site map, Harvest Barcode, diagnosis timeline, range cards,
  priority mixer, scenario sliders, Scout band panel, three lenses, mode badges and tappable
  source chips. Static fixture fallback works with the API stopped.
- Lead acceptance of B-01: three real POWER caches, 36 ingest tests green.
- L-04 Council core: bilingual glossary and blind spots, three constrained advisors, Number
  Auditor, audited Field Card with local QR and print HTML; 41 tests green.

**Next**

1. Human review: visual greyscale on `web/`, native Arabic review of `web/i18n/ar.json` and
   `content/`.
2. L-02 remainder: swap the real engine behind the unchanged result schema after B-02 acceptance.
3. L-05 after B-03/B-04: QA harness, provenance audit and validation wall.

**L-03 web evidence (at L-03 completion)**

```text
npm --prefix web run build     -> compiled, TypeScript clean, static /
headless Chrome 360 px         -> Arabic RTL + English LTR, scrollWidth 360, 0 console errors
static API-off fallback        -> bundled fixture, offline banner, no crash
interactions                   -> source-chip popover, lens switch, map select, scenario POST
python -m pytest               -> 151 passed at that checkpoint
python -m contracts.validate   -> 7/7 fixtures valid
```

The screen remains labelled illustrative. Visual greyscale and native Arabic review are still
human-only jobs and are not claimed as done.

**L-04 Council evidence**

```text
python -m pytest tests/council  -> 41 passed
bad claims                      -> 10/10 blocked (promise, forecast, unit, undeclared, source)
good claims                     -> 10/10 passed
Field Card length               -> 431 characters English, 445 Arabic
Field Card QR                   -> local SVG from segno, no network
provider failure                -> fixed-template fallback, never silent
```

Native Arabic review is still open and every Arabic content entry says
`needs_native_review: true`. The core is not yet wired into `api/` or `web/`.

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
- Repo-wide ruff has one Builder-owned unused import left until MSG-0014 is cleared.

---

## Agent B (Builder) — current handoff

**B-01 accepted:** three POWER caches (1991-01-01…2025-12-31, 0 missing days) and 36 passing
ingest tests. **B-02:** `REVIEW`, 28 engine tests green; replay 1.204 s and schema-valid.
**Active:** `B-03` economics, barcode and ranking.

**Owned paths:** `ingest/`, `engine/`, `data/cache/`, `data/prices.csv`, `scout/`, and matching
tests. **Never edits:** contracts, API, web, content, council, QA, docs, the board.

**Next checkpoint:** clear the two ruff errors in `engine/econ.py` and `tests/econ/test_econ.py`,
post B-03 acceptance evidence, then start B-04 fusion.

---

## Cross-folder requests

One open lint request to the Builder (MSG-0014): remove the unused `summarize_rotation` import
in `tests/econ/test_econ.py`. No contract change is requested. B-01 was accepted without one.

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
