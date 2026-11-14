# Changelog

All notable changes to AgroTwin are recorded here. The format follows Keep a Changelog and the
project uses Semantic Versioning. `VERSION` is the single source of truth.

## [Unreleased]

### Added

- Two-agent orchestration room in `agents/` with task board, contact log, status snapshot,
  decision log and a bootstrap prompt for the Builder.
- Gate 0 repository spine and tests.
- Fixture-backed FastAPI service: health, demo, diagnose, simulate, Scout intake, calibration
  and field card; every result is contract-validated and mode-tagged.
- Public `validate_document` for in-memory contract checks; API tests cover auth-before-body,
  duplicate runs, calibration minimums, schema validity and the 3-second demo budget.
- Bilingual Next.js 16 web app in `web/`: schematic site map, Harvest Barcode, diagnosis
  timeline, rotation cards with evidence/benefits/gaps/review flags, priority mixer, scenario
  sliders, Scout band narrowing, tappable source chips, mode badges, Farmer/Investor/Scientist
  lenses, Arabic RTL and English, and a bundled-fixture fallback that works without the API.
- Council core in `council/`: three constrained advisors with fixed-template fallback, a
  Number Auditor that blocks promises, undeclared numbers, unit mismatches and undeclared
  sources, and an audited Field Card with a local `segno` QR and bilingual print HTML.
- Bilingual `content/` library: glossary, ten blind spots, labels and advisor/Field Card
  templates. Arabic entries carry `needs_native_review: true`.

### Fixed

- Import ordering, line lengths and `zip(strict=...)` flagged by the first ruff run.

### Known limitations

- `api/` serves illustrative fixtures; the real engine swap waits on B-02.
- `/demo` supports only `delta_01` until the other caches and results exist.
- `web/` is labelled illustrative; its visual greyscale check and native Arabic review remain
  human jobs before Gate 3.
- The Council and Field Card core are not yet exposed through `api/` or `web/`; integration is
  scheduled for L-06. Arabic content is machine-written and awaits native review.

## [0.1.0] — 2026-11-14

### Added

- Product specification with P0 scope, three demo sites, units, gates and honest limits.
- Operating manual (`AGENTS.md`) with ownership, provenance, versioning and two-agent rules.
- Five frozen JSON Schemas at 1.0.0: `site`, `rotation`, `scout_run`, `replay`, `result`.
- Valid fixtures for every schema and a validator with cross-field invariants.
- Single-source version (`VERSION`), mirrored in `pyproject.toml` and `agrotwin.__version__`.
- Editable assumption ledger, soil-class table and provisional crop catalogue.
- FAO-56 Penman-Monteith ET0 with Hargreaves fallback and unit conversions.
- Interface stubs for water balance, replay, danger windows, fusion, bias check, twin,
  economics and ranking.
- Windows task runner (`tasks.ps1`), Makefile and CI workflow.
- AI-use disclosure log (`docs/AI_USE.md`) and gate checkpoint record (`HANDOFF.md`).

### Known limitations

- Crop coefficients and Egyptian planting windows are provisional and require verification.
- Prices are not yet sourced; the price table is a placeholder.
- No real POWER cache, Scout run, API result, web screen or QA result exists yet.
- The `result` fixture is illustrative and must not be presented as a site result.
