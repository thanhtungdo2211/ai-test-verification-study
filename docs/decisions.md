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
| D-006 | 2026-08-15 | Preserve the initial non-executable baseline attempt as `results/baseline/run-01-attempt-01/`; run the packaged candidate in canonical `results/baseline/run-01/`. | The runner correctly refused to overwrite the failed evidence. | Codex | Baseline evidence |
| D-007 | 2026-08-15 | Preserve mutation attempt 01 and rerun with `mutmut results --all true`. | Mutmut 3.7.0 requires an explicit boolean value for `--all`; the original wrapper command returned code 2 after mutation completed. | Codex | Mutation evidence |
| D-008 | 2026-08-17 | Preserve the supplied run-01 response as response-only evidence; do not reconstruct a missing session transcript or metadata. | The operator supplied implementation/tests but not the original prompt transcript, tool/model, timestamps, or operator fields. | TBD | `experiments/transcripts/run-01.response.txt` |

Add a new row for every deviation. Never rewrite an earlier row.
