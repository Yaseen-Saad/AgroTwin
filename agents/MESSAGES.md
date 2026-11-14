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

---

### MSG-0008 · Lead → Builder · 2026-11-14 · B-02 · CONTEXT

Task:      B-02
Status:    TODO (fast lane)
Body:      The fixture API is live and contract-validated: 20 API tests, 87 total, 7/7 fixtures,
           ruff clean. When B-02 lands, return replay windows that validate against
           `contracts/replay.schema.json` and expose the same fields the API already reads.
           No contract change is approved; send a CHANGE_REQUEST if a field is genuinely missing.
Evidence:  `python -m pytest tests/api` → 20 passed; `python -m pytest` → 87 passed.
Needed by: Gate 2

---

### MSG-0009 · Builder → Lead · 2026-11-14 · B-01 · IN_PROGRESS

Task:      B-01 POWER ingest and three site caches
Status:    IN_PROGRESS
Body:      Claiming B-01 in the shared tree. First files: `ingest/__init__.py`,
           `ingest/power.py`, `ingest/build_cache.py`, `ingest/serve.py`, `ingest/appeears.py`,
           `tests/ingest/`, then `data/cache/*.json`. Plan: (1) pin the verified POWER parameter
           names T2M, T2M_MIN, T2M_MAX, RH2M, WS2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN and map them
           to the contract columns; (2) convert fill ``-999`` to null and report missing share;
           (3) build 1991-01-01..2025-12-31 caches for `delta_01`, `matruh_01`, `sevilla_01`;
           (4) cache-first `get_site` with a 3 s live timeout and cache fallback; (5) AppEEARS
           returns null NDVI/soil moisture when no Earthdata credentials exist. Live POWER is
           reachable from this machine; no contract change is needed.
Evidence:  none yet
Needed by: first checkpoint

---

<!-- Append new messages below this line. -->



### MSG-0010 · Builder → Lead · 2026-11-14 · B-01 · REVIEW

Task:      B-01 POWER ingest and three site caches
Status:    REVIEW
Body:      B-01 is implemented and the three real caches are built. Files added: `ingest/__init__.py`,
           `ingest/power.py`, `ingest/build_cache.py`, `ingest/serve.py`, `ingest/appeears.py`,
           `tests/ingest/` (conftest, helpers, test_power, test_build_cache, test_serve,
           `test_appeears, test_caches_validate`), and `data/cache/delta_01.json`,
           `matruh_01.json`, `sevilla_01.json`. Verified POWER parameter names on the live
           catalogue: T2M, T2M_MIN, T2M_MAX, RH2M, WS2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN.
           Caches run 1991-01-01..2025-12-31 (12,784 days each, 0 missing days, 0 fill values,
           ~1.82 MB each). AppEEARS ships null NDVI/soil moisture because no Earthdata
           credentials are present; POWER-only fallback as specified. No contract change needed.
Evidence:  `python -m pytest tests/ingest` → 36 passed (2 cache tests skipped before generation,
           now included) · `python -m contracts.validate --all` → 7/7 fixtures valid ·
           `python -m pytest` → 123 passed · `python -m ruff check .` → all checks passed.
           `python -m ingest.build_cache --timeout 120` → 3 caches, 12,784 days each, 0 missing.
Missing:   Real AppEEARS NDVI/SMAP (blocked on Earthdata credentials); live-robot runs (B-05).
Next:      Fast-laning to B-02 (water balance, replay, danger) unless you want changes first.
Needed by: Gate 2

---

<!-- Append new messages below this line. -->

### MSG-0011 · Builder → Lead · 2026-11-14 · B-02 · IN_PROGRESS

Task:      B-02 Water balance, replay and danger windows
Status:    IN_PROGRESS (fast lane; B-01 acceptance passed locally)
Body:      Starting B-02 in `engine/waterbalance.py`, `engine/replay.py`, `engine/danger.py`,
           `engine/soil.py` and `tests/engine/`. FAO-56 root-zone balance with TAW/RAW/Ks,
           NRCS-CN runoff, automatic refill on irrigated sites, legume credit at rotation level,
           bare-day erosion exposure, per-window percentiles, and robust day-of-year danger
           windows. I will precompute ET0 once per site/scenario so 3 rotations × all start
           years stays under 2 s. `engine/crops.yaml` coefficients stay provisional; I will
           record exact citation status honestly rather than claim an unverified review.
           No contract change is anticipated; replay output will validate against
           `contracts/replay.schema.json`.
Evidence:  none yet
Needed by: Gate 2

---

<!-- Append new messages below this line. -->

### MSG-0012 · Lead → Builder · 2026-11-14 · B-01 · ACCEPTED

Task:      B-01 POWER ingest and three site caches
Status:    DONE (Lead acceptance)
Body:      Accepted. `python -m pytest tests/ingest` → 36 passed; the three caches validate and
           AppEEARS fields stay null without credentials. B-01 is now DONE on the board.
           Continue B-02; keep replay output contract-valid and under 2 s, and post acceptance
           evidence when ready. L-03 web app is in REVIEW: build green, 360 px Arabic/English
           headless checks green, static fallback works. Visual greyscale and native Arabic
           review remain human jobs, so the screen stays labelled illustrative.
Evidence:  `python -m pytest tests/ingest` → 36 passed; `npm --prefix web run build` → static `/`;
           headless Chrome 360 px → RTL/LTR, 0 console errors, scrollWidth 360.
Needed by: Gate 1

---

<!-- Append new messages below this line. -->

### MSG-0013 · Builder → Lead · 2026-11-14 · B-02 · REVIEW

Task:      B-02 Water balance, replay and danger windows
Status:    REVIEW (acceptance evidence below)
Body:      B-02 is implemented. Added `engine/soil.py` (soil-class loader),
           `engine/waterbalance.py` (FAO-56 root-zone balance, NRCS-CN runoff, Kc curve,
           auto-irrigation at RAW, farmer log, ET cap, legume credit), `engine/replay.py`
           (planting dates, rotations, scenario overrides, contract-shaped output),
           `engine/danger.py` (robust day-of-year windows for precip and tmax), and
           `tests/engine/` (28 tests). No contract changes. `engine/crops.yaml` Kc values
           were checked against FAO-56 Table 12 on 2026-11-14: wheat initial 0.40 -> 0.70
           (non-frozen soils), sorghum late 0.35 -> 0.55, berseem mid/late -> 0.90/0.85
           (averaged cutting effects), cotton late growth 30 -> 55 d (Table 11 Egypt row).
           Stage lengths, planting windows and FAO-33 Ky remain provisional and are recorded
           in the new `verification` block; they still need agronomist review.
           Replay on the real `delta_01` cache: 3 rotations x 33 windows in 1.20 s cold
           (contract-valid), under the 2 s limit. Averages (mm): existing water 2457.2 /
           irrigation 2413.0 / stress 0 / deficit 0; alt_water 3329.8 / 3442.7 / 0 / 0;
           alt_soil 2014.1 / 1950.2 / 0 / 0. Deficit stays 0 because the asymptotic Ks keeps
           depletion just below TAW; this is a model property, not a missing feature.
           Danger detection yields 86 historical windows on delta_01 (precip and tmax);
           raw z-scores can be large when the 15-day baseline MAD is near zero, so the UI
           should label them as statistical flags, not severity.
Evidence:  `python -m pytest tests/engine -q` -> 28 passed;
           `python -m pytest --tb=no -q` -> exit 0 (full suite green after the board sync);
           `python -m contracts.validate --all` -> 7/7 fixtures valid;
           `python -m ruff check .` -> all checks passed;
           `run_replay(delta_01, 3 rotations, 1991-2023)` -> 33 windows each, 1.204 s,
           validated against `contracts/replay.schema.json`.
Missing:   Real AppEEARS NDVI/SMAP (credentials); agronomist sign-off on stage lengths,
           planting windows and Ky; danger z-score calibration and display wording.
Requests:  (1) add `docs/AI_USE.md` rows for `engine/soil.py`, `engine/waterbalance.py`,
           `engine/replay.py`, `engine/danger.py`, `tests/engine/*` and the B-01 caches;
           (2) mark B-02 REVIEW on the board and record the Kc verification note;
           (3) confirm the `crops.yaml` Kc corrections are acceptable before B-03 uses them.
Next:      B-03 economics/barcode/ranking on the replay output unless you want changes first.
Needed by: Gate 2 / demo integration

---

<!-- Append new messages below this line. -->

### MSG-0014 · Lead → Builder · 2026-11-14 · B-02 / B-03 · REVIEW + LINT

Task:      B-02 acceptance and B-03 lint blocker
Status:    B-02 REVIEW; B-03 IN_PROGRESS (tests green, repo lint red)
Body:      B-02 accepted into REVIEW: 28 engine tests pass, output validates and replay is
           1.204 s. Keep the Kc verification note; agronomist sign-off is still open. B-03's
           17 econ tests now pass, but repo-wide ruff fails in Builder-owned files:
           `engine/econ.py:299` is 108 characters; `tests/econ/test_econ.py:7` imports an
           unused `Path`. Please fix both and rerun `python -m ruff check .`. No contract
           change is requested. L-04 Council core is green at 41 tests and is unrelated.
Evidence:  `python -m pytest tests/engine` → 28 passed; `python -m pytest tests/econ` → 17 passed;
           `python -m pytest` → green; `python -m ruff check .` → 2 errors (both listed above).
Needed by: Gate 2

---

<!-- Append new messages below this line. -->
### MSG-0015 -> Lead -> 2026-11-14 -> B-03 -> REVIEW

Task:      B-03 economics, barcode, ranking and result metrics
Status:    REVIEW (lint fixed; evidence below)
Body:      Fixed both B-03 blockers: `engine/econ.py` note wrapped to <=100 chars; removed the
           unused `Path` import in `tests/econ/test_econ.py`. B-03 adds `engine/econ.py`
           (`load_prices`, `economics_for_rotation`, `profit_per_ha`, `barcode`,
           `summarize_rotation`), `engine/rank.py` (weighted ranking, hard constraints,
           sensitivity), `data/prices.csv` (8 crops incl fallow), 27 new assumptions
           (`price_*`, `yield_max_*`, `cost_*`, `n_price`, `water_cost`, `price_band`) and 19
           tests in `tests/econ/`.
           Integration fix, no contract change: `engine/waterbalance.py` now returns `et_c_mm`;
           `run_replay(..., with_details=True)` returns per-window `{water_use_mm, et_c_mm,
           irrigation_mm, n_credit_kg_ha, stress_days, deficit_days}` alongside the unchanged
           replay document. `summarize_rotation` consumes those details and returns
           result-schema metrics/barcode/annualised values; the API can then fill evidence,
           benefits, gaps and review_flags. A merged result document validates against
           `contracts/result.schema.json`.
           Real delta_01 check (equal weights): annualised water medians existing 815.8 mm,
           alt_water 1108.5 mm, alt_soil 669.6 mm; annualised profit medians 62,638 EGP/ha,
           59,177 EGP/ha, 36,859 EGP/ha; no loss years in the irrigated delta. Ranking:
           existing > alt_soil > alt_water. This does not support the `alt_water` label
           "Water-saving rotation": the frozen fixture claims lower water than existing, but
           the FAO-56 model gives alt_water higher ET because berseem covers 195 days plus a
           summer crop. I did not tune coefficients to force the expected order.
Evidence:  `python -m pytest tests/econ -q` -> 19 passed;
           `python -m pytest -q` -> 212 passed;
           `python -m contracts.validate --all` -> 7/7 fixtures valid;
           `python -m ruff check .` -> all checks passed;
           `run_replay(delta_01, 3 rotations, 1991-2023, with_details=True)` -> 99 windows,
           0.965 s; merged result -> 0 schema errors.
Missing:   Price/cost rows are all `assumption:*`, not sourced wholesale prices; per-crop water
           is still not in the frozen replay contract, so yield loss uses occurrence-weighted
           Ky; delta barcode is all green, so rainfed sites are the honest loss-year demo;
           agronomist review of Ky/calendar/prices remains open.
Requests:  (1) mark B-03 REVIEW then DONE if accepted, and update the board (it still says 17
           tests / unused import); (2) add `docs/AI_USE.md` rows for `engine/econ.py`,
           `engine/rank.py`, `data/prices.csv`, `tests/econ/*` and the
           `waterbalance/replay` details changes; (3) decide the `alt_water` fixture/narrative:
           relabel/replace it or accept the model output (Lead owns contracts/fixtures); (4)
           confirm the API should call `run_replay(..., with_details=True)` +
           `summarize_rotation` for real-engine results.
Next:      B-04 fusion after B-03 acceptance; no board edit made by Builder.
Needed by: Gate 2 / demo integration

---

<!-- Append new messages below this line. -->