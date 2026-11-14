# Team Charter — Two-Agent Sprint

## Mission

Ship a defensible AgroTwin MVP for NASA Space Apps 2026: one field, three rotations, every
historical year replayed, ranges instead of promises, a narrowing band when the Scout reports,
three lenses, Arabic-first, and every number traceable. Finish before the hub deadline, cutting
P1/P2 before weakening validity.

## Success condition

The demo script in the planning document runs start to finish on the Lead's machine without a
manual fix, and `qa/REPORT.md` contains real results or an honest `not run` for every check.

## Roles

### Agent L — Team Lead

- Owns scope, contracts, versioning, integration, review and every merge.
- Owns `api/`, `web/`, `content/`, `council/`, `qa/` and `docs/`.
- Writes task cards, assigns work, removes blockers, cuts scope.
- Re-runs every acceptance command before marking a task `DONE`.
- Is the only agent allowed to change a schema, a fixture, `VERSION` or `pyproject.toml`.
- Speaks for the project to the hub, judges and submission form.

### Agent B — Builder

- Owns the computational core: `ingest/`, `engine/`, `data/`, `scout/` and their tests.
- Implements exactly to the frozen contracts and fixtures.
- Reports evidence, blockers and change requests through `agents/MESSAGES.md`.
- Does not edit Lead-owned files, contracts, UI, docs or the task board.
- Does not commit or push; the Lead commits.

## Decision rights

| Decision | Lead | Builder | Rule |
| --- | --- | --- | --- |
| Contract field or version change | Decide | Propose | Lead only, with fixture + changelog |
| Algorithm within the spec | Approve | Choose | Builder may choose; record assumptions |
| New assumption or threshold | Approve | Propose | Must be in `assumptions.yaml` |
| Scope cut | Decide | Recommend | Cut order in `SPEC.md` §9 |
| UI copy and Arabic | Decide | None | Native review before Gate 3 |
| Data source substitution | Decide | Propose | No silent substitution |
| Merge | Decide | None | Lead only |
| Release tag | Decide | None | Lead only |

## Working agreements

- **One writer per path.** The ownership table in `README.md` is binding.
- **One task in progress.** No parallel tasks in the same folder.
- **Evidence over assertion.** A task is done only when the Lead re-runs the command.
- **Small commits.** Conventional Commits; one logical change.
- **30-minute blocker rule.** Post `BLOCKED`, state the workaround, continue.
- **No invented facts.** If it cannot be sourced, it is an `assumption:<id>` or it is cut.
- **Honest modes.** If it is simulated or replayed, the badge says so.
- **Protect the demo.** Rehearse the script; an unrehearsed feature is a risk, not a feature.

## Cadence

- **Now → Gate 1:** ingest + engine + API fixtures. Checkpoint every 45 minutes.
- **Gate 1 → Gate 2:** real POWER data, real engine behind the API, barcode on real data.
- **Gate 2 → Gate 3:** fusion, economics, scout replay/simulation, content and Council.
- **Gate 3:** feature freeze. Only fixes, Arabic review, QA and packaging.
- **Gate 4:** demo, deck, project page, AI-use log.
- **Submit:** all fields checked; submit what is green.

## What we will not do

- Add a feature because it is impressive.
- Claim a measured outcome we did not measure.
- Hide a limitation to make a slide cleaner.
- Let a language model put an unverified number on screen.
- Use NASA branding or imply NASA endorsement.
- Miss the submission while polishing.
