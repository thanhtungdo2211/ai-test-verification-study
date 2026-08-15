# Experimental results

- `measurements.csv` is the canonical machine-readable summary.
- `baseline/run-XX/` stores AI-only pytest and coverage evidence.
- `mutation-ai-only/run-XX/` stores mutation results using only AI-generated tests.
- `mutation-independent/run-XX/` stores mutation results using the combined suite.
- `figures/` contains charts generated from canonical data.

Never overwrite a completed result directory. If a run is invalid, retain it, record the reason, and create a separately identified rerun according to the research protocol.

