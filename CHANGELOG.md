# Changelog

All notable changes to AgroTwin are recorded here. The format follows Keep a Changelog and the
project uses Semantic Versioning. `VERSION` is the single source of truth.

## [Unreleased]

### Added

- Two-agent orchestration room in `agents/` with task board, contact log, status snapshot,
  decision log and a bootstrap prompt for the Builder.
- Gate 0 repository spine and tests.

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
