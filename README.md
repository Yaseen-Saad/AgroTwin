# AgroTwin — from the sky to the land

AgroTwin replays decades of NASA POWER weather against three crop rotations for one field and
shows water, soil and profit outcomes as **ranges**, plus exactly what satellites cannot see.
Readings from the Verdex Scout re-weight the historical years so the band narrows.

Built for **NASA Space Apps 2026 — Field Shift: Adapting Farms with NASA Data**.

## Status

**Gate 0 passed; Gate 1 in progress.** Contracts, fixtures, versioning and the assumptions ledger
are frozen. The API serves contract-valid fixtures, the bilingual web app is built against
them, and the Council core audits its own Field Card. Real-engine integration, the Scout bridge
and full Council exposure through the API are still being built. Nothing on screen may be
presented as a validated site result until `qa/REPORT.md` records it.

- Two-agent build room: [`agents/`](agents/README.md)
- What we are building: [`SPEC.md`](SPEC.md)
- How to work here: [`AGENTS.md`](AGENTS.md)
- Gate checkpoints: [`HANDOFF.md`](HANDOFF.md)

## Quickstart

```powershell
.\tasks.ps1 install
.\tasks.ps1 validate
.\tasks.ps1 test
.\tasks.ps1 lint
.\tasks.ps1 api      # http://127.0.0.1:8000/docs
npm --prefix web install
.\tasks.ps1 web      # http://127.0.0.1:3000
```

GNU make users can run the equivalent targets: `make install`, `make validate`, `make test`,
`make lint`, `make api`, `make web`, `make version`.

The web app falls back to the bundled illustrative fixture when the API is unreachable. To point
it at another API, set `NEXT_PUBLIC_API_BASE` before building. To allow another web origin, set
`AGROTWIN_CORS_ORIGINS` on the API (default: `http://localhost:3000,http://127.0.0.1:3000`).

## Repository map

```text
SPEC.md  AGENTS.md  HANDOFF.md  VERSION  CHANGELOG.md
contracts/      frozen schemas, fixtures, validator
ingest/         POWER fetch, site caches, cache-first resolver
data/            cache files and price table
engine/         ET0, water balance, replay, danger, fusion, economics, ranking
api/            FastAPI service and Scout intake
web/            Next.js app, Arabic/English i18n, three lenses
scout/          ESP32 sketch, bridge, simulator, calibration, replay
council/        advisors and Number Auditor
content/        glossary, blind spots, result templates
qa/             validation wall, provenance audit, red-team report
docs/           methods, data sources, AI use, unit economics
tests/          contract, engine, API, Scout and coordination tests
agents/         two-agent task board and contact log
```

## Contracts

Five interfaces are frozen at schema version 1.0.0:

`site` · `rotation` · `scout_run` · `replay` · `result`

Validate every fixture and cross-field rule:

```powershell
python -m contracts.validate --all
```

## Honesty rules

- Every number carries `nasa:<product>`, `computed`, `scout:<run_id>`, `quoted:<url>` or
  `assumption:<id>`.
- Ranges, not promises. `LIVE`, `REPLAY`, `SIMULATED`, `NONE` are always visible.
- No rainfall forecast from POWER, no carbon-credit dollar figure, no field-level aquifer claim.
- AI use is disclosed in [`docs/AI_USE.md`](docs/AI_USE.md).
- No NASA logos, flags or mission insignia.

## Versioning

`VERSION` is the single source of truth and is mirrored in `pyproject.toml`,
`agrotwin.__version__` and `GET /health.version`. Gates are tagged `gate-N`; releases `vX.Y.Z`.
See `AGENTS.md` §6.

## License

To be confirmed by the team lead before submission. No license is granted by this file.
