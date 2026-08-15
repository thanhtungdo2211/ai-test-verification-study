# Reproduction scripts

These scripts operate on frozen artifacts and write new evidence; they do not
edit candidate source, transcripts, or the oracle.

## Independent test gate

Run the approved reference implementation and the three deliberate-fault
fixtures:

```bash
uv run python scripts/check_independent.py
```

The command must report that the reference passes and each faulty fixture is
rejected. `--reference-only` is useful while reviewing the oracle.

## Baseline tests

For a frozen candidate, run AI-only, independent, or combined tests. Existing
result directories are immutable:

```bash
uv run python scripts/run_tests.py --candidate run-01 --suite ai-only
uv run python scripts/run_tests.py --candidate run-01 --suite full
```

Each run stores `pytest.log`, JUnit counts, coverage JSON, and a manifest under
`results/baseline/run-XX/`.

## Mutation and aggregation

After a candidate and the required tests have been frozen, run mutation
separately for each suite. The wrapper uses a fresh temporary directory:

```bash
uv run python scripts/run_mutation.py --candidate run-01 --suite ai-only
uv run python scripts/run_mutation.py --candidate run-01 --suite full
```

After raw artifacts are present, rebuild the canonical CSV and dependency-free
SVG figures:

```bash
uv run python scripts/aggregate_results.py --force
uv run topic7 validate-data
```

`--force` only replaces generated `results/measurements.csv`; raw logs and
candidate artifacts are never overwritten.  Missing runs remain blank/`NA`.
