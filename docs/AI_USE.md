# AI Use Disclosure Log

This log is required by the NASA Space Apps submission. Every agent that generates code, data,
text or assets appends a row **in the same session** that produced the work. Never claim a human
reviewed something that was not reviewed.

> Rule: if a file exists, it has a row here. If a row says "pending", it has not been reviewed by
> a human and may not be described as reviewed in the submission.

## Summary

| Field | Value |
| --- | --- |
| Project | AgroTwin: from the sky to the land |
| Event | NASA Space Apps 2026 — Field Shift |
| Repository version | 0.1.0 |
| AI-use statement (short) | AI coding agents wrote code and documentation under human direction; all scientific claims are constrained to engine outputs; the Verdex classifier is prior work by its author. |
| Human reviewers | Pending: Lead review before Gate 3; native Arabic review before Gate 3 |

## Log

| Date | Agent | Tool / model | Files | What was generated | Human reviewer |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `SPEC.md` | Product specification, P0 scope, demo sites, contracts index, gates, limits | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `AGENTS.md` | Operating manual, ownership, provenance rules, version policy, two-agent mode | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `VERSION`, `pyproject.toml`, `CHANGELOG.md` (pending), `agrotwin/__init__.py` | Single-source version and package metadata | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `contracts/*.schema.json`, `contracts/README.md` | Five frozen JSON Schemas at 1.0.0 | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `contracts/fixtures/*.json` | Valid fixtures; clearly labelled illustrative data | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `contracts/validate.py`, `contracts/__init__.py` | Schema validation plus cross-field invariants | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `engine/et0.py`, `engine/units.py`, `engine/config.py`, `engine/crops.py` | FAO-56 ET0, unit conversions, assumption reader, provisional crop loader | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `engine/crops.yaml`, `engine/config/assumptions.yaml`, `engine/config/soil_classes.yaml` | Provisional coefficients and editable assumption ledger | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `engine/waterbalance.py`, `replay.py`, `danger.py`, `fusion.py`, `biascheck.py`, `twin.py`, `econ.py`, `rank.py` | Interface stubs with unit and contract references | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `ingest/*`, `api/*`, `web/*`, `scout/*`, `content/*`, `council/*` (as created) | Scaffolds and stubs; no scientific results | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `agents/README.md`, `CHARTER.md`, `TASKS.md`, `MESSAGES.md`, `STATUS.md`, `DECISIONS.md`, `prompts/builder-bootstrap.md` | Two-agent orchestration protocol and task board | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `HANDOFF.md`, `docs/AI_USE.md` | Gate checkpoint and disclosure log | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `README.md`, `CHANGELOG.md` | Project overview, quickstart and 0.1.0 changelog | Pending |
| 2026-11-14 | Agent L (Lead) | opencode / big-pickle | `tests/conftest.py`, `tests/test_version.py`, `tests/test_contracts.py`, `tests/test_et0.py`, `tests/test_units.py`, `tests/test_crops.py`, `tests/test_assumptions.py`, `tests/test_agents.py` | Version, contract, ET0, unit, crop, assumption and coordination tests; 67 passing | Pending |

## How to append

Use one row per logical change set:

```markdown
| 2026-11-14 | Agent B (Builder) | <tool / model> | `engine/waterbalance.py`, `tests/engine/test_balance.py` | FAO-56 daily balance and golden test | Pending |
```

Then add the same disclosure to the file itself:

- Python, shell, `.ino`: `# AI-generated under human review (<tool>, 2026-11-14). See docs/AI_USE.md.`
- TypeScript/TSX: `// AI-generated under human review (<tool>, 2026-11-14). See docs/AI_USE.md.`
- JSON/YAML/CSV: a `generated_by` field or leading row.
- Markdown/HTML: an HTML comment where appropriate.

## What AI must never do

- Put a number on screen that the engine did not compute.
- Present a historical replay as a forecast.
- Hide a `SIMULATED` or `REPLAY` source.
- Quote the Verdex classifier's accuracy without the author's held-out metric.
- Claim a human review, a pilot result or a customer that does not exist.
