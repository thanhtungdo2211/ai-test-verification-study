# Decision log

Record protocol decisions here before the first official candidate run.  Each
entry should include the date, decision owner, rationale, and whether it
changes a frozen artifact.

| ID | Date (UTC) | Decision | Rationale/evidence | Owner | Frozen artifact affected |
|---|---|---|---|---|---|
| D-001 | 2026-08-15 | Use Python 3.12 and the dependency versions in `uv.lock`. | One interpreter and lockfile make reruns comparable. | TBD | `pyproject.toml`, `uv.lock` |
| D-002 | 2026-08-15 | Target six runs: two tools/models with three clean runs each. | Recommended design in the project plan; retain every failed run. | TBD | `experiments/metadata.csv` |
| D-003 | 2026-08-15 | Use the standardized follow-up only after an explicit clarification question. | Prevents operator hints from changing the treatment. | TBD | `spec/ambiguous-requirement.md` |
| D-004 | 2026-08-15 | Treat timeout and error as reported mutant states, never as killed. | Preserves the denominator and avoids optimistic scores. | TBD | `results/measurements.csv` |
| D-005 | 2026-08-15 | Freeze oracle v1.0 with SHA-256 `0e618183e836ee7b293a11159fe941e25c4659068ce1b321c24980b32f97d25f`. | Hash is recorded before candidate generation; named M1/M3 signatures remain pending. | TBD | `spec/acceptance-oracle.md` |

Add a new row for every deviation. Never rewrite an earlier row.
