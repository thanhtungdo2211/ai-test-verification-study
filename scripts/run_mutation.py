#!/usr/bin/env python3
"""Run mutmut in an isolated copy of one frozen candidate.

The wrapper prevents caches and generated mutants from leaking between the
AI-only and full-suite configurations. It deliberately refuses to overwrite
existing evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

RUN_ID_PATTERN = re.compile(r"run-\d{2}")
ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, help="candidate ID such as run-01")
    parser.add_argument("--suite", required=True, choices=("ai-only", "full"))
    parser.add_argument("--max-children", type=int, default=1)
    return parser.parse_args()


def hash_python_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for source in sorted(path.rglob("*.py")):
        digest.update(source.relative_to(path).as_posix().encode())
        digest.update(source.read_bytes())
    return digest.hexdigest()


def copy_required_tree(source: Path, destination: Path, label: str) -> None:
    if not source.is_dir() or not any(source.rglob("*.py")):
        raise FileNotFoundError(f"{label} is missing Python files: {source}")
    shutil.copytree(source, destination)


def mutmut_config(test_paths: list[str]) -> str:
    selection = ", ".join(json.dumps(path) for path in test_paths)
    copied = ", ".join(json.dumps(path) for path in test_paths)
    return f"""[tool.pytest.ini_options]
pythonpath = ["src"]

[tool.mutmut]
source_paths = ["src"]
also_copy = [{copied}]
pytest_add_cli_args = ["--import-mode=prepend"]
pytest_add_cli_args_test_selection = [{selection}]
use_git_change_detection = false
"""


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    args = parse_args()
    if not RUN_ID_PATTERN.fullmatch(args.candidate):
        raise SystemExit("--candidate must match run-XX")
    if args.max_children < 1:
        raise SystemExit("--max-children must be positive")

    candidate = ROOT / "candidates" / args.candidate
    output_group = "mutation-ai-only" if args.suite == "ai-only" else "mutation-independent"
    output = ROOT / "results" / output_group / args.candidate
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to overwrite existing evidence: {output}")
    output.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(UTC)
    with tempfile.TemporaryDirectory(prefix=f"topic7-{args.candidate}-{args.suite}-") as temp:
        work = Path(temp)
        copy_required_tree(candidate / "src", work / "src", "candidate source")
        copy_required_tree(candidate / "tests_ai", work / "tests_ai", "AI-generated tests")

        test_paths = ["tests_ai"]
        if args.suite == "full":
            copy_required_tree(
                ROOT / "tests_independent",
                work / "tests_independent",
                "independent tests",
            )
            test_paths.append("tests_independent")

        config = mutmut_config(test_paths)
        (work / "pyproject.toml").write_text(config, encoding="utf-8")
        (output / "mutmut-config.toml").write_text(config, encoding="utf-8")

        baseline = run_command(
            [sys.executable, "-m", "pytest", "-q", *test_paths],
            cwd=work,
        )
        (output / "baseline.log").write_text(baseline.stdout, encoding="utf-8")
        if baseline.returncode != 0:
            return_code = baseline.returncode
            mutation = None
            results = None
            export = None
        else:
            mutation = run_command(
                [
                    sys.executable,
                    "-m",
                    "mutmut",
                    "run",
                    "--max-children",
                    str(args.max_children),
                ],
                cwd=work,
            )
            (output / "mutation.log").write_text(mutation.stdout, encoding="utf-8")
            results = run_command(
                [sys.executable, "-m", "mutmut", "results", "--all"],
                cwd=work,
            )
            (output / "results.txt").write_text(results.stdout, encoding="utf-8")
            export = run_command(
                [sys.executable, "-m", "mutmut", "export-cicd-stats"],
                cwd=work,
            )
            stats = work / "mutants" / "mutmut-cicd-stats.json"
            if stats.is_file():
                shutil.copy2(stats, output / "mutmut-cicd-stats.json")
            return_code = mutation.returncode

    manifest = {
        "candidate": args.candidate,
        "suite": args.suite,
        "started_at": started_at.isoformat(),
        "ended_at": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "mutmut": importlib.metadata.version("mutmut"),
        "candidate_python_sha256": hash_python_tree(candidate),
        "baseline_returncode": baseline.returncode,
        "mutation_returncode": None if mutation is None else mutation.returncode,
        "results_returncode": None if results is None else results.returncode,
        "export_returncode": None if export is None else export.returncode,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if return_code != 0:
        print(f"Mutation run failed; inspect {output}", file=sys.stderr)
    else:
        print(f"Mutation evidence written to {output}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
