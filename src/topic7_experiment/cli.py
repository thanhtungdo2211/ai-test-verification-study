"""Command-line interface for experiment maintenance tasks."""

from __future__ import annotations

import argparse
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
    raise AssertionError(f"unhandled command: {args.command}")
