# Topic 7 — AI-generated code and test verification

Reproducible Python research project for the IT4490 group essay:

> How can a team break the loop “AI misunderstands the requirement → writes incorrect code → writes tests that prove the incorrect code is correct”?

This repository is the experimental evidence package. The official submissions remain the 12–18 page report and the presentation of at most 15 slides.

## Important experiment rule

Do **not** give a repository-aware coding agent access to this repository during the official candidate-generation runs. The project documents describe the hidden oracle. Each candidate must be produced in a clean chat/context that receives only [the frozen public prompt](experiments/prompts/ambiguous-requirement.txt).

Candidate implementation is intentionally absent from the initial scaffold. It must be generated during the controlled experiment, not authored in advance.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Git

## Local setup

```bash
uv sync --locked
uv run pytest
uv run ruff check .
uv run topic7 validate-data
```

Or run the complete local quality gate:

```bash
make check
```

## Repository map

```text
.
├── candidates/                 # Frozen outputs from run-01 ... run-06
├── docs/                       # Course brief, project spec, and execution plan
├── experiments/
│   ├── prompts/                # Public prompt supplied to coding AI
│   └── transcripts/            # Raw AI transcripts
├── private/                    # Git-ignored oracle before runs are frozen
├── report/                     # Report sources and generated figures
├── results/                    # Measurements, coverage, and mutation evidence
├── scripts/                    # Reproduction helpers
├── slides/                     # Presentation sources
├── spec/                       # Public experiment protocol
├── src/topic7_experiment/      # Research metrics and validation harness
├── tests/                      # Harness tests
└── tests_independent/          # Independent acceptance/property test suite
```

## Controlled workflow

1. Requirement Owner and Independent Verifier freeze the oracle outside the AI-visible context.
2. AI Operator executes six clean candidate runs with the identical public prompt.
3. Candidate code, AI-generated tests, assumptions, and transcripts are frozen.
4. Independent tests are frozen before the verifier opens candidate code/tests.
5. The team runs AI-only tests, independent tests, coverage, and mutation testing.
6. Scripts generate measurements and figures from raw evidence.
7. The team publishes the oracle with the final evidence package after the experiment.

The independent-suite gate can be checked before candidate runs with
`uv run python scripts/check_independent.py`.  Once candidate artifacts exist,
`scripts/run_tests.py` records immutable baseline logs and
`scripts/aggregate_results.py --force` rebuilds the CSV and SVG figures.

Full details:

- [Project specification](docs/topic7-project-spec.md)
- [Execution plan](docs/topic7-project-plan.md)
- [AI operator run guide](docs/ai-run-operator-guide.md)
- [GitHub issue/PR candidate workflow](docs/github-candidate-pr-workflow.md)
- [Evaluation runbook](docs/evaluation-runbook.md)
- [Contribution guide](CONTRIBUTING.md)

## Data validation

`topic7 validate-data` checks the headers and basic integrity of:

- `experiments/metadata.csv`
- `results/measurements.csv`

It exits non-zero when required fields or inconsistent score inputs are found.

## AI-use disclosure

Every AI-assisted artifact must record the tool, displayed model, timestamp, prompt/transcript, purpose, operator, and any human edits. Do not place unverifiable AI-generated claims or citations in the report.
