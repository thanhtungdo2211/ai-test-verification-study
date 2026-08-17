# Synthetic evaluation snapshot

This is a checked-in pipeline rehearsal produced by
`scripts/run_synthetic_demo.py`. It contains no external AI observations:

- `run-01` uses the existing reference fixture with a sparse synthetic suite;
- `run-02` uses the same reference fixture with a broader synthetic suite;
- all metadata explicitly says `SYNTHETIC-DEMO` and `NOT-AN-AI-RUN`.

Permitted uses:

- verify CSV/table/chart formatting;
- rehearse baseline and mutation commands;
- draft report section structure and placeholder captions;
- demonstrate that independent tests can change mutation detection in a pilot.

Forbidden uses:

- copy rows into canonical experiment files;
- report these scores as AI-generated experimental findings;
- use the pilot to answer RQ1, RQ2 or RQ3;
- present pilot charts as final submission evidence.

Every table or figure copied into a draft must be labelled
`PILOT — SYNTHETIC, NOT RESEARCH DATA` and replaced by generated official data
before submission.

Validate the snapshot with:

```bash
uv run topic7 validate-data --root pilot/synthetic-evaluation
```

Regenerate a fresh local rehearsal outside this tracked snapshot with:

```bash
uv run python scripts/run_synthetic_demo.py
```
