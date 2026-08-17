#!/usr/bin/env python3
"""Create and evaluate two isolated synthetic runs for pipeline rehearsal.

The generated artifacts live outside the canonical candidate and result trees.
They are not research observations and must never enter the report dataset.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

from topic7_experiment.validation import METADATA_HEADERS

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMO_ROOT = REPOSITORY_ROOT / ".synthetic-evaluation"

SYNTHETIC_TESTS_RUN_01 = '''"""Sparse synthetic tests; not AI evidence."""

from transfer_fee import calculate_transfer_fee


def test_minimum_fee():
    assert calculate_transfer_fee(1) == 5_000


def test_regular_fee():
    assert calculate_transfer_fee(1_000_000) == 10_000


def test_vip_fee():
    assert calculate_transfer_fee(1_000_000, is_vip=True) == 8_000
'''

SYNTHETIC_TESTS_RUN_02 = '''"""Broader synthetic tests; not AI evidence."""

import pytest

from transfer_fee import calculate_transfer_fee


@pytest.mark.parametrize(
    ("amount", "is_vip", "expected"),
    [
        (1, False, 5_000),
        (1, True, 4_000),
        (500_000, False, 5_000),
        (1_000_000, False, 10_000),
        (1_000_000, True, 8_000),
        (1_050_000, False, 11_000),
        (5_000_000, False, 50_000),
        (10_000_000, True, 40_000),
    ],
)
def test_examples(amount, is_vip, expected):
    assert calculate_transfer_fee(amount, is_vip) == expected


@pytest.mark.parametrize("amount", [0, -1])
def test_non_positive_amount(amount):
    with pytest.raises(ValueError):
        calculate_transfer_fee(amount)


@pytest.mark.parametrize("amount", [True, 1.0, "1000", None])
def test_invalid_amount_type(amount):
    with pytest.raises(TypeError):
        calculate_transfer_fee(amount)


def test_invalid_vip_type():
    with pytest.raises(TypeError):
        calculate_transfer_fee(1_000_000, is_vip=1)
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_DEMO_ROOT,
        help="isolated output root (must not already contain files)",
    )
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_reference_candidate(
    demo_root: Path, run_id: str, synthetic_tests: str, description: str
) -> None:
    destination = demo_root / "candidates" / run_id
    package = destination / "src" / "transfer_fee"
    package.mkdir(parents=True)

    reference_package = REPOSITORY_ROOT / "tests_independent" / "reference_impl" / "transfer_fee"
    calculator = (reference_package / "calculator.py").read_text(encoding="utf-8")
    calculator = calculator.replace(
        "from tests_independent.oracle import reference_transfer_fee",
        "from .oracle import reference_transfer_fee",
    )
    write_text(package / "calculator.py", calculator)
    shutil.copy2(reference_package / "__init__.py", package / "__init__.py")
    shutil.copy2(REPOSITORY_ROOT / "tests_independent" / "oracle.py", package / "oracle.py")

    write_text(destination / "tests_ai" / "test_calculator.py", synthetic_tests)
    write_text(
        destination / "ASSUMPTIONS.md",
        "# SYNTHETIC DEMO\n\nNo AI assumptions exist; this is a local fixture.\n",
    )
    write_text(
        destination / "README.md",
        f"# SYNTHETIC DEMO {run_id}\n\n"
        "Uses the existing independent reference fixture and synthetic tests.\n"
        f"{description}\n"
        "This is not AI evidence.\n",
    )


def copy_run_01(demo_root: Path) -> None:
    copy_reference_candidate(
        demo_root,
        "run-01",
        SYNTHETIC_TESTS_RUN_01,
        "The sparse suite demonstrates how independent tests can improve mutation detection.",
    )


def copy_run_02(demo_root: Path) -> None:
    copy_reference_candidate(
        demo_root,
        "run-02",
        SYNTHETIC_TESTS_RUN_02,
        "The broader suite exercises successful AI-only and full mutation paths.",
    )


def write_metadata(demo_root: Path) -> None:
    transcript_dir = demo_root / "experiments" / "transcripts"
    for run_id in ("run-01", "run-02"):
        write_text(
            transcript_dir / f"{run_id}.response.txt",
            "SYNTHETIC PIPELINE DEMO — NO AI SESSION OCCURRED.\n",
        )

    metadata = demo_root / "experiments" / "metadata.csv"
    metadata.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, run_id in enumerate(("run-01", "run-02"), start=1):
        rows.append(
            {
                "run_id": run_id,
                "tool": "SYNTHETIC-DEMO",
                "model_displayed": "NOT-AN-AI-RUN",
                "started_at": f"2000-01-01T00:00:0{index}Z",
                "ended_at": f"2000-01-01T00:00:1{index}Z",
                "context_clean": "NA",
                "clarification_asked": "NA",
                "ambiguities_detected": "NA",
                "followup_used": "NA",
                "human_edits": "NA",
                "raw_response_path": f"experiments/transcripts/{run_id}.response.txt",
                "transcript_path": f"experiments/transcripts/{run_id}.response.txt",
                "operator": "local-synthetic-fixture",
            }
        )
    with metadata.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def run(command: list[str], *, expected: set[int] | None = None) -> int:
    expected_codes = expected or {0}
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=REPOSITORY_ROOT, check=False)
    if completed.returncode not in expected_codes:
        raise RuntimeError(
            f"command returned {completed.returncode}, expected {sorted(expected_codes)}: {command}"
        )
    return completed.returncode


def main() -> int:
    args = parse_args()
    demo_root = args.root.resolve()
    if demo_root.exists() and any(demo_root.iterdir()):
        raise SystemExit(
            f"refusing to overwrite synthetic evidence: {demo_root}; choose a new --root"
        )
    demo_root.mkdir(parents=True, exist_ok=True)
    write_text(
        demo_root / "SYNTHETIC_NOT_RESEARCH_DATA.md",
        "# Synthetic pipeline rehearsal\n\n"
        "No external AI runs produced this data. It may be used to rehearse the\n"
        "pipeline and draft report layout only. Do not present it as research.\n",
    )
    copy_run_01(demo_root)
    copy_run_02(demo_root)
    shutil.copytree(REPOSITORY_ROOT / "tests_independent", demo_root / "tests_independent")
    write_metadata(demo_root)

    for run_id in ("run-01", "run-02"):
        run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "run_tests.py"),
                "--root",
                str(demo_root),
                "--candidate",
                run_id,
                "--suite",
                "ai-only",
            ]
        )
        run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "run_tests.py"),
                "--root",
                str(demo_root),
                "--candidate",
                run_id,
                "--suite",
                "full",
            ],
            expected={0, 1},
        )
        run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "run_mutation.py"),
                "--root",
                str(demo_root),
                "--candidate",
                run_id,
                "--suite",
                "ai-only",
            ]
        )
        run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts" / "run_mutation.py"),
                "--root",
                str(demo_root),
                "--candidate",
                run_id,
                "--suite",
                "full",
            ],
            expected={0, 1},
        )

    run(
        [
            sys.executable,
            str(REPOSITORY_ROOT / "scripts" / "aggregate_results.py"),
            "--root",
            str(demo_root),
            "--force",
        ]
    )
    run(
        [
            sys.executable,
            "-m",
            "topic7_experiment",
            "validate-data",
            "--root",
            str(demo_root),
        ]
    )
    print(f"Synthetic demo completed: {demo_root}")
    print(f"Measurements: {demo_root / 'results' / 'measurements.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
