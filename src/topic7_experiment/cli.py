"""Command-line interface for experiment maintenance tasks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from topic7_experiment.validation import validate_default_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="topic7")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-data", help="validate canonical evidence CSV files")
    validate.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (defaults to the current directory)",
    )
    aggregate = subparsers.add_parser(
        "aggregate-results", help="rebuild measurements and figures from raw evidence"
    )
    aggregate.add_argument("--root", type=Path, default=Path.cwd())
    aggregate.add_argument(
        "--force", action="store_true", help="replace the generated measurements.csv"
    )
    independent = subparsers.add_parser(
        "check-independent", help="check the oracle suite and deliberate faults"
    )
    independent.add_argument("--reference-only", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate-data":
        issues = validate_default_data(args.root)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("Experiment CSV files are valid.")
        return 0
    if args.command == "aggregate-results":
        command = [
            sys.executable,
            str(Path(__file__).resolve().parents[2] / "scripts" / "aggregate_results.py"),
            "--root",
            str(args.root),
        ]
        if args.force:
            command.append("--force")
        return subprocess.run(command, check=False).returncode
    if args.command == "check-independent":
        command = [
            sys.executable,
            str(Path(__file__).resolve().parents[2] / "scripts" / "check_independent.py"),
        ]
        if args.reference_only:
            command.append("--reference-only")
        return subprocess.run(command, check=False).returncode
    raise AssertionError(f"unhandled command: {args.command}")
