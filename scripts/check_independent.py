#!/usr/bin/env python3
"""Check that independent tests pass on the reference and fail on known faults."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = [
    str(ROOT / "tests_independent" / "test_acceptance.py"),
    str(ROOT / "tests_independent" / "test_properties.py"),
]
PYTHON = (
    str(ROOT / ".venv" / "bin" / "python")
    if (ROOT / ".venv" / "bin" / "python").is_file()
    else sys.executable
)


def run_target(module: str, extra_path: Path) -> tuple[int, str]:
    environment = os.environ.copy()
    environment["TOPIC7_TARGET_MODULE"] = module
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(extra_path), str(ROOT), environment.get("PYTHONPATH", "")]
    )
    result = subprocess.run(
        [PYTHON, "-m", "pytest", "-q", *SUITE],
        cwd=ROOT,
        env=environment,
        text=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-only", action="store_true")
    args = parser.parse_args()
    reference_root = ROOT / "tests_independent" / "reference_impl"
    reference_status, reference_output = run_target("transfer_fee.calculator", reference_root)
    if reference_status != 0:
        print("reference implementation did not pass independent tests", file=sys.stderr)
        print(reference_output, file=sys.stderr)
        return 1
    if args.reference_only:
        return 0

    faults = (
        "faulty_discount_order",
        "faulty_bankers_rounding",
        "faulty_bool_validation",
    )
    for fault in faults:
        status, _ = run_target(f"tests_independent.fixtures.{fault}", ROOT)
        if status == 0:
            print(f"independent tests unexpectedly accepted {fault}", file=sys.stderr)
            return 1
    print("Reference implementation passed; all deliberate faults were detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
