# Live Task Board

> Last updated: 2026-11-14 12:10 Cairo · Gate 0 · Version 0.1.0
> Board owner: **Agent L**. Status changes are made by the Lead after evidence is reviewed.
> One `IN_PROGRESS` task per agent. P0 before P1; anything not green is cut, not extended.

## Current sprint

| Track | Active task | Status | Next |
| --- | --- | --- | --- |
| Lead (L) | `L-01` Gate 0 spine and green build | `REVIEW` (green; commit/tag human-gated) | `L-02` API on fixtures |
| Builder (B) | `B-01` POWER ingest and 3 caches | `ASSIGNED` | `B-02` water balance and replay |

## Board

| ID | Owner | Wave | Pri | Task | Depends on | Status |
| --- | --- | --- | --- | --- | --- | --- |
| L-01 | L | 0 | P0 | Gate 0 spine, version, tests, tags | — | `REVIEW` |
| B-01 | B | 0 | P0 | POWER ingest, 3 site caches, fallback | L-01 contracts | `ASSIGNED` |
| L-02 | L | 1 | P0 | API endpoints on fixtures, then real engine | L-01, B-02 | `TODO` |
| L-03 | L | 1 | P0 | Web app: map, barcode, mixer, sliders, lenses | L-01, L-02 fixtures | `TODO` |
| B-02 | B | 1 | P0 | FAO-56 water balance, replay, danger windows | L-01, B-01 | `TODO` |
| B-03 | B | 2 | P0 | Economics, barcode class, ranking, prices | B-02 | `TODO` |
| B-04 | B | 2 | P0 | Fusion, bias check, twin experiment | B-02 | `TODO` |
| L-04 | L | 2 | P0 | Glossary, blind spots, templates, Number Auditor | L-02 shape | `TODO` |
| B-05 | B | 3 | P0 | Scout simulator, calibration, bridge, replay, ESP32 | L-01 contracts | `TODO` |
| L-05 | L | 3 | P0 | QA harness, provenance audit, validation wall | B-02, B-03, B-04 | `TODO` |
| L-06 | L | 3 | P0 | Integration, demo rehearsal, release tags | all P0 | `TODO` |
| B-06 | B | 4 | P0 | Real-data performance and regression hardening | B-01…B-05 | `TODO` |
| L-07 | L | 4 | P0 | Submission fields, deck, video, AI-use audit | L-06 | `TODO` |

Legend: `TODO` · `ASSIGNED` · `IN_PROGRESS` · `BLOCKED` · `REVIEW` · `CHANGES_REQUESTED` ·
`DONE` · `CUT`.

---

## Lead tasks

### L-01 · Gate 0 spine and green build

**Status:** `REVIEW` · **Wave:** 0 · **Priority:** P0

**Evidence.** `python -m contracts.validate --all` → 7/7 fixtures valid ·
`python -m pytest` → 67 passed · `python -m ruff check .` → all checks passed. The `gate-0` tag
and the first commit are human-gated and not yet created.

**Goal.** Finish the repository spine: `HANDOFF.md`, `docs/AI_USE.md`, assumptions ledger, tests
for version/contracts/ET0/units/crops, green validate + test + lint, and the `gate-0` tag.

**Paths.** root files, `contracts/`, `tests/` (root tests only), `agents/`, `docs/AI_USE.md`.

**Definition of done.**
- `python -m contracts.validate --all` validates every fixture.
- `python -m pytest` passes.
- `python -m ruff check .` passes.
- `VERSION`, `pyproject.toml` and `agrotwin.__version__` agree.
- `HANDOFF.md` records the Gate 0 checkpoint and human blockers.
- `docs/AI_USE.md` has the bootstrap entry.
- `gate-0` tag created; working tree clean.

**Acceptance command.**

```powershell
python -m contracts.validate --all; python -m pytest; python -m ruff check .
```

---

### L-02 · API endpoints on fixtures, then real engine

**Status:** `TODO` · **Wave:** 1 · **Priority:** P0

**Goal.** FastAPI service with `/health`, `/demo/{site}`, `POST /diagnose`, `POST /simulate`,
`POST /scout/run`, `POST /scout/calibrate`, `POST /fieldcard`. Serve fixtures first, then swap
the real engine behind the same result schema without breaking the frontend.

**Paths.** `api/`, `tests/api/`.

**Definition of done.**
- Every response matches the contract and carries `mode` and source tags.
- Scout intake requires a bearer token and a mode; bad token rejected before body parsing.
- Result cache keyed by `(site_id, rotations, scenario, scout_run_ids)`.
- `/demo/delta_01` returns a precomputed result in under 3 seconds.
- No schema changes; requests go in `MESSAGES.md`.

**Acceptance command.**

```powershell
python -m pytest tests/api
```

---

### L-03 · Frontend and lenses

**Status:** `TODO` · **Wave:** 1 · **Priority:** P0

**Goal.** Next.js app built against fixtures: pin drop, diagnosis timeline, Harvest Barcode,
three rotation cards with evidence/benefits/gaps/review flags, priority mixer, scenario sliders,
Scout panel with band narrowing, mode badge, source chips, Farmer/Investor/Scientist lenses,
Arabic RTL and English, 360 px.

**Paths.** `web/`.

**Definition of done.**
- `npm --prefix web run build` passes.
- Static demo mode works with no network from the fixture result.
- Every number is tappable and shows its source tag.
- Arabic is default RTL; strings live only in `web/i18n/ar.json` and `en.json`.
- Mode badge is visible on every screen.
- Manual 360 px and greyscale check recorded in `MESSAGES.md`.

**Acceptance command.**

```powershell
npm --prefix web run build
```

---

### L-04 · Content, Council and Number Auditor

**Status:** `TODO` · **Wave:** 2 · **Priority:** P0

**Goal.** Bilingual glossary, blind-spot library, result templates, Field Card (print + WhatsApp
< 600 chars + local QR), three advisors with fixed-template fallback and a Number Auditor that
blocks undeclared or mismatched numbers.

**Paths.** `content/`, `council/`, `tests/council/`.

**Definition of done.**
- `content/glossary.json` and `content/blindspots.json` contain Arabic and English.
- Arabic entries carry `needs_native_review: true` until signed off.
- 10 seeded bad claims blocked, 10 good claims passed.
- WhatsApp text under 600 characters in both languages.
- LLM provider optional; failure always falls back to templates.

**Acceptance command.**

```powershell
python -m pytest tests/council
```

---

### L-05 · QA harness, provenance audit, validation wall

**Status:** `TODO` · **Wave:** 3 · **Priority:** P0

**Goal.** `qa/validation_wall.py` runs hindcast, twin experiment, real-robot check, vision
metrics and Council audit. A provenance audit fails on any untagged number or hard-coded UI
string. A sanity suite checks ranking, legume credit, fallow, price and fusion identity.
`qa/REPORT.md` holds real results or `not run` with a reason.

**Paths.** `qa/`, `tests/qa/`.

**Definition of done.**
- `python -m qa.validation_wall` prints a machine-readable report.
- `qa/REPORT.md` is never pre-written with results.
- The hostile-judge weakness list is ranked by damage to Validity.
- Provenance audit scans API output and UI strings.

**Acceptance command.**

```powershell
python -m qa.validation_wall
python -m pytest tests/qa
```

---

### L-06 · Integration, demo rehearsal and release

**Status:** `TODO` · **Wave:** 3 · **Priority:** P0

**Goal.** Merge every green Builder task, run the demo script twice, fix integration defects,
bump the version, tag `gate-3` / `gate-4` / `v0.2.0`, and keep `HANDOFF.md` current.

**Paths.** root, `HANDOFF.md`, `CHANGELOG.md`, `VERSION`, `pyproject.toml`.

**Definition of done.**
- Full merge checklist green.
- Demo steps 1-9 run from the script without manual fixes.
- Every result on stage is labelled LIVE, REPLAY or SIMULATED.
- Release notes and version agree.

**Acceptance command.**

```powershell
python -m contracts.validate --all; python -m pytest; python -m ruff check .
```

---

### L-07 · Submission fields, deck and video

**Status:** `TODO` · **Wave:** 4 · **Priority:** P0

**Goal.** Complete every submission field, 7-slide deck, 30-second video with English subtitles,
project page text, AI-use disclosure, and the prior-work declaration for Verdex.

**Paths.** `docs/`, submission drafts.

**Definition of done.**
- No claim in the deck that `qa/REPORT.md` has not confirmed.
- Arabic copy reviewed by a native reader.
- AI-use log complete and consistent with code/data headers.
- Hub deadline confirmed; submission submitted with time to spare.

**Acceptance.** Manual doc audit against the official submission guide.

---

## Builder tasks

### B-01 · POWER ingest and three site caches

**Status:** `ASSIGNED` · **Wave:** 0 · **Priority:** P0

**Goal.** Build `ingest/power.py` (daily point API, exact parameter catalogue lookup, fill-value
handling), `ingest/build_cache.py`, `ingest/serve.py` (cache-first, 3 s live timeout, fallback)
and the optional `ingest/appeears.py` time-box. Produce schema-valid caches for `delta_01`,
`matruh_01` and `sevilla_01` from 1991-01-01 to the last complete year.

**Paths.** `ingest/`, `data/cache/`, `tests/ingest/`.

**Definition of done.**
- Parameter names verified against the POWER catalogue and recorded in a module constant.
- Missing days and missing-value share reported.
- Every cache validates against `contracts/site.schema.json`.
- Live fetch failure falls back to cache within 3 seconds (mocked network test).
- AppEEARS failure is logged; fields ship as `null` rather than invented.
- No raw large data committed beyond the three JSON caches.

**Acceptance command.**

```powershell
python -m pytest tests/ingest; python -m contracts.validate --all
```

---

### B-02 · Water balance, replay and danger windows

**Status:** `TODO` · **Wave:** 1 · **Priority:** P0

**Goal.** Implement `engine/waterbalance.py`, `engine/replay.py` and `engine/danger.py` exactly
to Agent guide §5.1, §5.2 and §5.6, using `engine/et0.py`, `engine/crops.yaml` and
`engine/config/soil_classes.yaml`. Verify every coefficient and record the source.

**Paths.** `engine/waterbalance.py`, `engine/replay.py`, `engine/danger.py`, `engine/crops.yaml`,
`tests/engine/`.

**Definition of done.**
- Hand-computed golden case passes within the stated tolerance.
- Water balance closes within 1 mm.
- Fallow has zero transpiration and counts bare days.
- Identical input gives identical output.
- Three rotations over all windows run in under 2 seconds on a cached site.
- Output validates against `contracts/replay.schema.json`.
- No contract edits; requests go through `MESSAGES.md`.

**Acceptance command.**

```powershell
python -m pytest tests/engine
```

---

### B-03 · Economics, barcode and ranking

**Status:** `TODO` · **Wave:** 2 · **Priority:** P0

**Goal.** Implement `engine/econ.py` and `engine/rank.py`; fill `data/prices.csv` for every
candidate crop with a source URL or an `assumption:<id>` and a year. Profit per hectare per
historical year, low/base/high price scenarios, Ky yield loss, legume fertilizer saving, barcode
class, worst year, loss-year share, weighted ranking and hard-constraint exclusion.

**Paths.** `engine/econ.py`, `engine/rank.py`, `data/prices.csv`, `tests/econ/`.

**Definition of done.**
- Profit falls when price falls; legume always earns a credit; excluded rotation never ranks.
- Ranking changes sensibly when weights move; tie band reported.
- Every price and cost row carries a year and a source or assumption tag.
- No price forecast; price shock is a user input.

**Acceptance command.**

```powershell
python -m pytest tests/econ
```

---

### B-04 · Fusion, bias check and twin experiment

**Status:** `TODO` · **Wave:** 2 · **Priority:** P0

**Goal.** Implement `engine/fusion.py`, `engine/biascheck.py`, `engine/twin.py` to Agent guide
§5.3 and §5.4. Weighted analog ensemble, ESS guard, calibration gate, post-wetting filter,
irrigation-log gate, SMAP bias check, twin coverage report.

**Paths.** `engine/fusion.py`, `engine/biascheck.py`, `engine/twin.py`, `tests/fusion/`.

**Definition of done.**
- Zero readings → uniform weights and unchanged range.
- Consistent synthetic readings → range narrows.
- ESS never below the floor; widening sigma never narrows the range.
- Refuses without a calibration id, or without an irrigation log on an irrigated site.
- `python -m engine.twin` prints coverage, width ratio and ESS distribution, or an honest
  `not_run` reason.

**Acceptance command.**

```powershell
python -m pytest tests/fusion; python -m engine.twin
```

---

### B-05 · Scout simulator, calibration, bridge and firmware

**Status:** `TODO` · **Wave:** 3 · **Priority:** P0

**Goal.** Implement `scout/simulator.py` (SIMULATED only), `scout/calibrate.py` (rejects fewer
than 3 samples), `scout/bridge.py` (serial + Ali's model wrapper), `scout/replay/` (REPLAY
conversion) and the ESP32 sketch with `config.example.h`. Mark the sketch UNTESTED ON HARDWARE
until Ali confirms.

**Paths.** `scout/`, `tests/scout/`.

**Definition of done.**
- Every generated run validates against `contracts/scout_run.schema.json`.
- Mode is always set and never silently changed.
- Calibration rejects < 3 samples and writes a calibration id.
- Simulator never emits LIVE or REPLAY.
- No Wi-Fi credentials, tokens or `config.h` committed.

**Acceptance command.**

```powershell
python -m pytest tests/scout
```

---

### B-06 · Real-data performance and regression hardening

**Status:** `TODO` · **Wave:** 4 · **Priority:** P0

**Goal.** After the real engine is behind the API, profile and harden: 20+ years × 3 rotations
under 2 seconds, API under 3 seconds, cache fallback verified, determinism preserved, edge cases
(missing humidity/wind/solar, leap years, polar latitudes, fallow-only rotations, duplicate
Scout points) covered by tests.

**Paths.** engine-owned and ingest-owned files plus their tests.

**Definition of done.**
- Performance budget measured on the lead's machine and recorded.
- Regression tests added for every bug found during integration.
- No new assumptions without a ledger entry.

**Acceptance command.**

```powershell
python -m pytest; python -m contracts.validate --all
```

---

## Wave plan

| Wave | Gate | Lead | Builder | Exit condition |
| --- | --- | --- | --- | --- |
| 0 | Gate 0 | L-01 | B-01 | Contracts, tests and spine green; caches started |
| 1 | Gate 1-2 | L-02, L-03 | B-02 | Fixture app end-to-end; real engine on real caches |
| 2 | Gate 2-3 | L-04 | B-03, B-04 | Barcode, economics, fusion, content and auditor |
| 3 | Gate 3-4 | L-05, L-06 | B-05 | Feature freeze, QA report, scout replay |
| 4 | Submit | L-07 | B-06 | Submission complete; submit what is green |

## Cut order (never cut P0)

1. Live WhatsApp bot.
2. Open-Meteo seasonal weighting.
3. Sub-field zones and cooperative mode.
4. Agronomist handoff page.
5. Plain-English toggle (keep glossary tooltips).
6. SMAP comparison slide.

If the hub deadline is earlier than Sunday 20:00, compress waves 3 and 4; do not add work.
