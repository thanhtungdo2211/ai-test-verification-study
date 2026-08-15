# Contributing

## Branches

- `main`: reproducible, reviewed experiment state.
- `setup/*`: research harness and repository configuration.
- `run/*`: packaging of one frozen AI run; never mix candidates.
- `analysis/*`: data aggregation, figures, and report analysis.

## Pull requests

Every pull request must state:

- whether it changes the prompt, oracle, candidate output, test logic, or only packaging;
- which raw artifact or research decision authorizes the change;
- commands used for verification;
- whether AI assisted the change and where its transcript is stored.

Candidate business logic and AI-generated expected values must not be manually corrected. A packaging-only change needs a patch entry in `experiments/packaging-fixes.csv`.

## Local quality gate

```bash
uv sync --locked
uv run pre-commit install
make check
```

Run every pre-commit hook against the repository with:

```bash
uv run pre-commit run --all-files
```

## Evidence discipline

- Never overwrite a raw transcript or result log.
- Use `run-01` through `run-06` consistently in every artifact.
- Use ISO 8601 timestamps with a timezone.
- Store missing measurements as empty/`NA`, not zero.
- Do not classify a mutant as equivalent without a written justification and reviewer.
- Do not expose the hidden oracle to candidate-generating AI.
