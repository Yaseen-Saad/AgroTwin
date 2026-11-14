# Contracts

Five frozen interfaces connect the AgroTwin agents. Code against these files and their fixtures,
never against another agent's implementation.

| Schema | Version | Producer | Consumers |
| --- | --- | --- | --- |
| `site.schema.json` | 1.0.0 | Agent 1 | Agents 2, 4, 7 |
| `rotation.schema.json` | 1.0.0 | Web / API | Agent 2 |
| `scout_run.schema.json` | 1.0.0 | Agent 9 / simulator | Agents 4, 5, 7 |
| `replay.schema.json` | 1.0.0 | Agent 2 | Agents 3, 4, 7 |
| `result.schema.json` | 1.0.0 | Agents 3/4/5 | Web, content, QA |

## Validate

```bash
python -m contracts.validate --all
python -m contracts.validate --schema result
```

The validator checks JSON Schema plus cross-field invariants that schemas cannot express
(column/row alignment, percentile ordering, barcode years, tag presence, ranking membership).

## Change control

- Additive optional field → minor schema version bump, new fixture, `CHANGELOG.md` entry.
- Rename, removal or type change → major bump, migration note, lead approval.
- Never edit a released fixture in place; add a new one and note the migration.
- Assumption tags must exist in `engine/config/assumptions.yaml`.

## Conventions

- UTF-8, two-space indent, trailing newline.
- Timestamps ISO-8601 UTC (`Z` or `+00:00`).
- Engine units: hectares, millimetres, EGP, UTC.
- `generated_by` is required on every data instance.
- `mode` is required wherever Scout data can appear.
- No NASA logos, flags or mission insignia.
