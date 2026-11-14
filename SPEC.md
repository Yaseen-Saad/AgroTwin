# AgroTwin — Product Specification

| Field | Value |
| --- | --- |
| Project | AgroTwin: from the sky to the land |
| Challenge | NASA Space Apps 2026 — Field Shift: Adapting Farms with NASA Data |
| Document version | 1.0.0 |
| Repository version | 0.1.0 (`VERSION`) |
| Current gate | Gate 0 — bootstrap complete |
| Status | Contracts frozen for Gate 0; engine, API, web and scout modules are scaffolds |
| Owner | Agent 0 (Lead) |
| Last updated | 2026-11-14 |

This file is the single source of truth for **what** is being built. Implementation rules live in
`AGENTS.md`. Data contracts live in `contracts/`. Handoffs live in `HANDOFF.md`.

---

## 1. Product

AgroTwin lets a farmer test a crop rotation against the weather their own field has actually
lived through. For one pinned field it replays every historical year of NASA POWER weather
through a daily water balance for three rotations (the farmer's current rotation plus two
alternatives) and reports water, soil and profit outcomes as **ranges**, not point promises.

Readings from the Verdex Scout — a small field robot with soil, rain and air sensors and a
plant-health camera — re-weight the historical years so the outcome range narrows. Every result
is presented through three lenses (Farmer, Investor, Scientist) in Arabic or English, with a
Harvest Barcode of good and bad years, a blind-spots card, and a printable Field Card.

**Pitch line.** AgroTwin replays 20+ years of NASA-derived weather against three rotations for
one field, then shows the range of water, soil and profit outcomes, plus exactly what satellites
cannot see.

**Tagline.** From the sky to the land.

**Non-negotiable.** AgroTwin supports farmers and agronomists. It does not replace their
judgment, and it never presents a historical replay as a forecast.

---

## 2. Problem and why now

Egypt's renewable freshwater is almost entirely Nile-dependent, agriculture consumes the
majority of withdrawals, and most holdings are small. A wrong rotation risks a household's
income for a season, so farmers rationally repeat last year's choice even when water or soil no
longer supports it. Existing dashboards show data but not the risk of a decision.

Sourced figures used in the pitch (verify before publication):

- Under 490 m³ of water per person per year versus the UN scarcity threshold of 1,000 m³
  (Ahram Online, 2026-02-08).
- Agriculture accounted for 79% of Egypt's water withdrawals in 2020 (AGBI).
- 4.1 million holdings under 5 feddans in 2010, up from 877,000 in 1950 (FAO brief).
- Agriculture is about 15% of GDP; Egypt imports about 40% of its food (Business Monthly).

These figures are quoted material, not engine outputs. They must carry a `quoted:` source tag
wherever they appear in the product.

---

## 3. MVP scope (P0)

Build P0 completely before touching P1. Anything not green at a gate is cut, not extended.

| # | P0 capability | Definition of done |
| --- | --- | --- |
| P0-1 | Pin a field; three rotations (existing + two alternatives) | Any lat/lon resolves to a cached site or a live POWER fetch with cache fallback |
| P0-2 | Replay every historical year since 1991 | Every start year simulated for all three rotations in under 2 s |
| P0-3 | Evidence, benefits, data gaps and local-review flags | Every rotation card renders all four sections from structured result fields |
| P0-4 | Priority mixer and scenario sliders | Water/soil/profit weights re-rank; rain, warming and price sliders re-run the engine |
| P0-5 | Verdex Scout fusion | A Scout run re-weights years, narrows the range, and displays ESS and confidence |
| P0-6 | Harvest Barcode | One stripe per historical year per rotation with green/amber/red class |
| P0-7 | Judge lenses and bilingual UI | Farmer, Investor, Scientist views; Arabic RTL and English; feddans and EGP |
| P0-8 | Provenance and honesty layer | Every number has a tappable source tag; persistent LIVE/REPLAY/SIMULATED badge |

### P1 (only after all P0 is green)

Plant sightings on the timeline, Council advisors with Number Auditor, Field Card with QR and
WhatsApp text, plain-English toggle, agronomist handoff page.

### P2 (mockups in the pitch only, never built this weekend)

Live WhatsApp bot, sub-field zones, cooperative pooling, carbon estimate.

---

## 4. Non-goals and explicit non-claims

- No rainfall forecast is produced from NASA POWER. POWER is historical and near-real-time only.
  Forward-looking weather is a user-set scenario, or an explicitly disclosed P1 Open-Meteo
  seasonal add-on.
- No trained "digital twin" model is claimed. The engine is a transparent physical simulator
  with a historical-analog ensemble.
- No commodity price forecast. Prices are sourced constants or labelled assumptions, with
  low/base/high user scenarios.
- No carbon-credit revenue claim.
- No live WhatsApp bot in the MVP.
- No claim of measured yield gain, water saving or revenue. Those require a pilot.
- No NASA logos, flags or mission insignia in generated material.

---

## 5. Demo sites

Coordinates are the lead's proposal and require approval. Each cache will run 1991-01-01 to the
last complete calendar year once Agent 1 lands real POWER data.

| site_id | Name | Role | lat | lon | Elevation | Irrigation | Soil class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `delta_01` | Mansoura, Nile Delta | Irrigated, high-input reference | 31.0409 | 31.3785 | 8 m | irrigated | clay_loam |
| `matruh_01` | Marsa Matruh hinterland | Dry, rain-reliant Egyptian site | 31.3543 | 27.2373 | 30 m | rainfed | sandy_loam |
| `sevilla_01` | Seville, Andalusia, Spain | Non-Egyptian proof that the pipeline is portable | 37.3891 | -5.9845 | 10 m | rainfed | clay_loam |

Use `matruh_01` for the Scout demo: fusion on an irrigated site requires a farmer-supplied
irrigation log, which a casual demo will not have.

---

## 6. Architecture

Data flows one way. No screen computes a scientific number; no language model invents one.

```text
NASA POWER ─┐
MODIS/SMAP ─┼─> data/cache ─> engine (ET0, water balance, replay, fusion, economics, rank)
Open-Meteo* ┘                       │
                                    v
Verdex Scout ─> scout bridge ─> api/ (FastAPI) ─> web/ (Next.js, three lenses)
                                    │
                              council/ (templates, optional LLM + Number Auditor)
```

`*` Open-Meteo is a P1, non-NASA add-on and must be labelled whenever enabled.

Optional layers fail closed:

- If Earthdata access fails, the engine runs on POWER weather alone and `monthly_ndvi` /
  `monthly_soil_moisture` are `null`.
- If Scout hardware is unavailable, the demo uses a REPLAY of earlier real logs or a SIMULATED
  run. The mode badge always says which.

---

## 7. Contracts, units and provenance

The three base contracts plus the two v2 additions are frozen at Gate 0 in `contracts/`:

| Contract | Schema | Producer | Consumers |
| --- | --- | --- | --- |
| Site cache | `site.schema.json` | Agent 1 | Agents 2, 4, 7 |
| Rotation request | `rotation.schema.json` | Web/API | Agent 2 |
| Scout run | `scout_run.schema.json` | Agent 9 / simulator | Agents 4, 5, 7 |
| Replay metrics | `replay.schema.json` | Agent 2 | Agents 3, 4, 7 |
| Result | `result.schema.json` | Agents 3/4/5 | Web, content, QA |

**Units.** The engine works in hectares, millimetres and EGP. One feddan = 0.42 ha
(≈ 4,200 m²). The API adds per-feddan values; the Farmer lens shows feddans and EGP.

**Source tags.** Every number carries exactly one of:

```text
nasa:<product>        computed        scout:<run_id>
quoted:<url>          assumption:<tag>
```

Assumption defaults live in `engine/config/assumptions.yaml`. Untagged numbers fail QA.

**Modes.** `LIVE | REPLAY | SIMULATED | NONE` travel with the data end to end. `NONE` means no
Scout data was used. The badge is always visible in the UI.

---

## 8. AI design

The AI is in four auditable places, each with a baseline and a fallback:

1. **Historical-analog replay** — physics, no training. Baseline: one average year. The spread
   of outcomes is the value.
2. **Sensor–satellite fusion** — ensemble re-weighting with ESS guard. Baseline: unweighted
   ensemble. Measured by interval width and twin-experiment coverage.
3. **Verdex plant-health classifier** — prior work by Ali Kotb-Mostafa Dawood. Only the author's
   held-out accuracy and confusion matrix may be quoted.
4. **Council explainer** — constrained language model that may only restate engine outputs. The
   Number Auditor blocks any undeclared or mismatched number and falls back to fixed templates.

Full algorithms are specified in the planning document, Agent guide §5. Implementation must not
diverge without a spec change recorded in `CHANGELOG.md`.

---

## 9. Validation wall

Agent 7 runs these; results are never pre-written. `qa/REPORT.md` is the only place they appear.

1. **Hindcast** — modelled stress ranking vs an independent satellite signal; report n and
   Spearman rho, even if weak.
2. **Twin experiment** — hide one year, generate noisy Scout-like readings, check whether truth
   falls in the weighted 80% interval. Report coverage (target 70-90%), interval-width ratio and
   ESS distribution.
3. **Real-robot check** — plot real Verdex and satellite/model values on overlapping days.
4. **Vision metrics** — the author's own held-out accuracy and confusion matrix, verbatim.
5. **Council audit** — numbers generated, traced, blocked.

A check that cannot run prints `not run` and the reason. Stating a limit scores better than
hiding it.

---

## 10. Judge criteria mapping

Official names: **Influence, Creativity, Validity, Relevance, Presentation**.

| Criterion | What the judge can point to |
| --- | --- |
| Influence | A farmer-sized decision under water stress; portable to any POWER location; low-bandwidth Field Card |
| Creativity | Every historical year replayed per rotation; Harvest Barcode; first-class blind-spots card |
| Validity | FAO-56 water balance; source chip on every number; ranges; golden cases; published limits |
| Relevance | 3+ strategies including the existing one; evidence; benefits; gaps; local review; plain English; scenarios |
| Presentation | One story from question to Field Card; subtitles; no unexplained jargon |

---

## 11. Gates

All times Cairo. A gate passes only when the checks run green on the lead's machine.

| Gate | When | Must be true |
| --- | --- | --- |
| 0 | Sat 13:00 | Spec, schemas, fixtures, Makefile, sites committed; `make test` green |
| 1 | Sat 16:00 | App runs end to end on fixtures; simulator narrows the band; Ali's samples received |
| 2 | Sat 19:00 | Real POWER caches for 3 sites; real engine behind the API; barcode on real data |
| 3 | Sun 09:00 | Feature freeze; reviewed Arabic; Council + auditor; first real QA report |
| 4 | Sun 14:00 | Demo recorded with English subtitles; deck and project page complete; AI_USE complete |
| Submit | Sun 20:00 | Every form field checked; submit what is green |

If the hub deadline is Saturday night, merge waves 2 and 3, drop Sunday phases, and submit by
Saturday 19:00.

---

## 12. Versioning and change control

- **SemVer** `MAJOR.MINOR.PATCH` for the repository, single-sourced in `VERSION` and mirrored in
  `pyproject.toml`. `agrotwin.__version__` reads `VERSION`; `/health` reports it.
- Contracts carry `"x-schema-version": "1.0.0"`. A breaking schema change requires a major bump,
  a new fixture, and an entry in `CHANGELOG.md`.
- Git tags: `gate-0`, `gate-1`, ... for gates; `v0.1.0`, `v0.2.0`, ... for releases.
- Only the lead merges. Every merge runs `make validate`, `make test`, `make lint`.
- Any deviation from the algorithms in the planning document must be recorded in
  `CHANGELOG.md` and approved by the lead before merge.

---

## 13. Open verification items

These are explicitly unverified and must be checked before their dependent gate:

- Exact POWER parameter names for evapotranspiration and soil wetness (Agent 1).
- Earthdata / AppEEARS product names and extract workflow (Agent 1).
- Crop coefficients, planting windows, Ky values and Egyptian price/cost rows (Agents 2, 3;
  agronomist review).
- Verdex dataset size ("30,0000" in the source file is ambiguous), held-out accuracy and
  confusion matrix (Ali; Agent 8).
- GRACE-FO footprint (regional context only; do not claim field-level aquifer health).
- Hub deadline and prior-work declaration rules (Lead; human job).
- Open-Meteo terms of use before the P1 add-on ships.

---

## 14. Responsible AI and limits

Each limit below must also appear in the product:

- Satellites cannot see subsurface pH, salinity, nematode load, local input availability or
  water rights. The Field Card lists them for local review.
- History is not a forecast; a new extreme may fall outside the replay.
- A cheap soil probe reads one spot and must be calibrated on the actual soil. Fusion refuses to
  run without a calibration id.
- Plant-health sightings are observations, not diagnoses.
- AI advisors restate engine outputs only; the Number Auditor enforces it.
- The farmer owns the field data and can export it.
- AI assistance is disclosed in `docs/AI_USE.md` and in the submission's AI-use field.
