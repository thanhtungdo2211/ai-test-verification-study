# Experiment records

The official run record is append-only and uses the same `run-XX` identifier in
metadata, candidates, transcripts, baseline logs, mutation output, and report
tables.

Before each run, the operator records the displayed tool/model and UTC times in
`metadata.csv`.  After the response is saved unchanged, the operator stores
the candidate layout described in `candidates/README.md`, computes checksums,
and records any packaging-only patch in `packaging-fixes.csv`.

The public prompt in `prompts/ambiguous-requirement.txt` is frozen.  Do not add
follow-up text unless the AI asks for clarification, and then use only the
standard response documented in `spec/ambiguous-requirement.md`.

## Evaluation after candidates are merged

For the detailed baseline, independent-test, coverage, mutation and aggregation
sequence, see [`docs/evaluation-runbook.md`](../docs/evaluation-runbook.md).
The short command sequence for each executable candidate is:

```bash
uv run python scripts/run_tests.py --candidate run-XX --suite ai-only
uv run python scripts/run_tests.py --candidate run-XX --suite full
uv run python scripts/run_mutation.py --candidate run-XX --suite ai-only
uv run python scripts/run_mutation.py --candidate run-XX --suite full
```

Then regenerate the machine-readable summary:

```bash
uv run python scripts/aggregate_results.py --force
uv run topic7 validate-data
```

The AI-only raw mutation score is `killed_ai / mutants_total_ai * 100`. The
full-suite score uses the corresponding `*_full` columns. Timeout and error are
reported separately and are never counted as killed. Never overwrite an
existing result directory; preserve failed attempts and record the reason.
