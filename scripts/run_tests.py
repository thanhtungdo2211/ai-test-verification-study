#!/usr/bin/env python3
"""Run one frozen candidate's tests and write immutable baseline evidence.

The runner is intentionally a small subprocess wrapper.  It never edits a
candidate and refuses to overwrite an existing result directory.  The same
command can run AI-only tests, independent tests, or both suites together.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_ID_PATTERN = re.compile(r"run-\d{2}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="candidate ID such as run-01")
    parser.add_argument("--suite", choices=("ai-only", "independent", "full"), default="ai-only")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--timeout", type=float, default=300.0, help="pytest timeout in seconds (default: 300)"
    )
    return parser.parse_args(argv)


def _non_negative_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def parse_junit(path: Path) -> dict[str, int]:
    """Extract stable test counts from pytest's JUnit XML output."""

    if not path.is_file():
        return {"collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return {"collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return {"collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    counts = {
        key: _non_negative_int(suite.attrib.get(xml_name)) or 0
        for key, xml_name in (
            ("collected", "tests"),
            ("failed", "failures"),
            ("errors", "errors"),
            ("skipped", "skipped"),
        )
    }
    counts["passed"] = max(
        0, counts["collected"] - counts["failed"] - counts["errors"] - counts["skipped"]
    )
    return counts


def parse_coverage(path: Path) -> dict[str, float | None]:
    """Read line/branch percentages from a coverage.py JSON report."""

    if not path.is_file():
        return {"line_coverage": None, "branch_coverage": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        totals = data.get("totals", {}) if isinstance(data, dict) else {}
        if not isinstance(totals, dict):
            return {"line_coverage": None, "branch_coverage": None}
        line = totals.get("percent_covered")
        branch = totals.get("percent_covered_branches")
        return {
            "line_coverage": round(float(line), 2) if line is not None else None,
            "branch_coverage": round(float(branch), 2) if branch is not None else None,
        }
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return {"line_coverage": None, "branch_coverage": None}


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def run_candidate(
    candidate: Path,
    output: Path,
    suite: str,
    *,
    timeout: float,
    python_executable: str = sys.executable,
) -> int:
    """Execute one suite and write evidence; return pytest's status code."""

    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite existing evidence: {output}")

    started_at = datetime.now(UTC)
    source = candidate / "src"
    ai_tests = candidate / "tests_ai"
    independent_tests = candidate.parent.parent / "tests_independent"
    if not source.is_dir():
        _write_text(output / "pytest.log", f"candidate source is missing: {source}\n")
        _write_manifest(output, candidate, suite, started_at, None, 2, {}, {}, "non-executable")
        return 2

    test_paths: list[Path] = []
    if suite in {"ai-only", "full"}:
        test_paths.append(ai_tests)
    if suite in {"independent", "full"}:
        test_paths.append(independent_tests)
    missing = [str(path) for path in test_paths if not path.is_dir()]
    if missing:
        message = "missing test directories: " + ", ".join(missing) + "\n"
        _write_text(output / "pytest.log", message)
        _write_manifest(output, candidate, suite, started_at, None, 2, {}, {}, "non-executable")
        return 2

    with tempfile.TemporaryDirectory(prefix=f"topic7-{candidate.name}-{suite}-") as temp_dir:
        temporary = Path(temp_dir)
        junit = temporary / "junit.xml"
        coverage = temporary / "coverage.json"
        relative_paths = [
            str(path.relative_to(candidate)) if path.is_relative_to(candidate) else str(path)
            for path in test_paths
        ]
        command = [
            python_executable,
            "-m",
            "pytest",
            "-q",
            "--junitxml",
            str(junit),
            "--cov=src",
            "--cov-branch",
            f"--cov-report=json:{coverage}",
            *relative_paths,
        ]
        environment = os.environ.copy()
        path_entries = [str(source), str(candidate), str(candidate.parent.parent)]
        environment["PYTHONPATH"] = os.pathsep.join(
            [*path_entries, environment.get("PYTHONPATH", "")]
        )
        try:
            completed = subprocess.run(
                command,
                cwd=candidate,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=timeout,
            )
            return_code = completed.returncode
            log = completed.stdout
            status = "completed" if return_code == 0 else "tests_failed"
        except subprocess.TimeoutExpired as exc:
            return_code = 124
            partial = exc.stdout or ""
            if isinstance(partial, bytes):
                partial = partial.decode(errors="replace")
            log = partial + f"\npytest timed out after {timeout:g} seconds\n"
            status = "timeout"
        _write_text(output / "pytest.log", log)
        if junit.is_file():
            output.joinpath("junit.xml").write_bytes(junit.read_bytes())
        if coverage.is_file():
            output.joinpath("coverage.json").write_bytes(coverage.read_bytes())
        test_counts = parse_junit(junit)
        coverage_counts = parse_coverage(coverage)

    _write_manifest(
        output,
        candidate,
        suite,
        started_at,
        command,
        return_code,
        test_counts,
        coverage_counts,
        status,
    )
    return return_code


def _write_manifest(
    output: Path,
    candidate: Path,
    suite: str,
    started_at: datetime,
    command: list[str] | None,
    return_code: int,
    test_counts: dict[str, int],
    coverage_counts: dict[str, float | None],
    status: str,
) -> None:
    manifest = {
        "candidate": candidate.name,
        "suite": suite,
        "started_at": started_at.isoformat(),
        "ended_at": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "command": command,
        "returncode": return_code,
        "status": status,
        **test_counts,
        **coverage_counts,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if not RUN_ID_PATTERN.fullmatch(args.candidate):
        raise SystemExit("--candidate must match run-XX")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    root = args.root.resolve()
    candidate = root / "candidates" / args.candidate
    baseline_root = root / "results" / "baseline" / args.candidate
    output = baseline_root if args.suite == "ai-only" else baseline_root / args.suite
    try:
        return run_candidate(candidate, output, args.suite, timeout=args.timeout)
    except FileExistsError as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
