# Repository instructions for coding agents

## Scope

This repository is an academic experiment about AI-generated code and tests. Preserve the validity and traceability of its evidence.

## Rules

- Do not generate or modify candidate business logic unless the user explicitly identifies an official controlled run.
- Never alter `experiments/prompts/ambiguous-requirement.txt` after it is frozen without recording a protocol deviation.
- Do not infer or expose the hidden acceptance oracle to a candidate-generating context.
- Never overwrite raw transcripts, baseline logs, mutation logs, or frozen candidate artifacts.
- A packaging-only candidate fix must be recorded in `experiments/packaging-fixes.csv`.
- Keep `run-XX` identifiers consistent across candidates, transcripts, results, and report data.
- Generated tables and charts must come from raw data; do not hand-edit reported measurements.
- Use Python 3.12, uv, pytest, Hypothesis, pytest-cov, mutmut, and Ruff as configured in `pyproject.toml`.
- Run `make check` before handing off a repository change.

