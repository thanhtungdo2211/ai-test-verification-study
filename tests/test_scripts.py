from __future__ import annotations

import json
from pathlib import Path

from scripts.aggregate_results import (
    acceptance_counts,
    generate_figures,
    measurement_row,
    parse_mutation_evidence,
    write_measurements,
)
from scripts.run_mutation import mutmut_config
from scripts.run_tests import parse_coverage, parse_junit
from topic7_experiment.validation import MEASUREMENT_HEADERS, METADATA_HEADERS


def test_parse_junit_and_coverage(tmp_path: Path) -> None:
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuite tests="3" failures="1" errors="0" skipped="1">'
        '<testcase name="test_acceptance_example" />'
        '<testcase name="test_acceptance_bad"><failure /></testcase>'
        '<testcase name="test_property"><skipped /></testcase>'
        "</testsuite>",
        encoding="utf-8",
    )
    coverage = tmp_path / "coverage.json"
    coverage.write_text(
        json.dumps({"totals": {"percent_covered": 91.25, "percent_covered_branches": 80.0}}),
        encoding="utf-8",
    )

    assert parse_junit(junit) == {
        "collected": 3,
        "passed": 1,
        "failed": 1,
        "errors": 0,
        "skipped": 1,
    }
    assert acceptance_counts(junit) == (1, 2, 0)
    assert parse_coverage(coverage) == {"line_coverage": 91.25, "branch_coverage": 80.0}


def test_measurement_row_uses_raw_manifests(tmp_path: Path) -> None:
    metadata = dict.fromkeys(METADATA_HEADERS, "")
    metadata["run_id"] = "run-01"
    baseline = tmp_path / "results" / "baseline" / "run-01"
    baseline.mkdir(parents=True)
    (baseline / "manifest.json").write_text(
        json.dumps({"collected": 4, "passed": 3, "line_coverage": 88.5, "branch_coverage": 70.0}),
        encoding="utf-8",
    )
    mutation = tmp_path / "results" / "mutation-ai-only" / "run-01"
    mutation.mkdir(parents=True)
    (mutation / "manifest.json").write_text(
        json.dumps({"killed": 7, "survived": 2, "timeout": 1, "error": 0, "equivalent": 1}),
        encoding="utf-8",
    )

    row = measurement_row(tmp_path, metadata)
    assert row["ai_tests_collected"] == "4"
    assert row["line_coverage"] == "88.5"
    assert row["mutants_total_ai"] == "10"
    assert row["raw_score_ai"] == "70"
    assert row["adjusted_score_ai"] == "87.5"
    assert parse_mutation_evidence(mutation).total is None


def test_parse_mutmut_statuses_keeps_timeout_and_non_killed_states(tmp_path: Path) -> None:
    stats = tmp_path / "mutmut-cicd-stats.json"
    stats.write_text(
        json.dumps(
            {
                "killed": 7,
                "survived": 2,
                "total": 10,
                "no_tests": 0,
                "skipped": 0,
                "suspicious": 0,
                "timeout": 1,
                "segfault": 0,
            }
        ),
        encoding="utf-8",
    )

    evidence = parse_mutation_evidence(tmp_path)
    assert evidence.error == 0
    assert evidence.timeout == 1
    assert evidence.total == 10


def test_write_measurements_and_figures(tmp_path: Path) -> None:
    row = {name: ("run-01" if name == "run_id" else "") for name in MEASUREMENT_HEADERS}
    output = tmp_path / "results" / "measurements.csv"
    write_measurements(output, [row], force=False)
    generate_figures(tmp_path, [row])
    assert output.is_file()
    assert (tmp_path / "results" / "figures" / "mutation-scores.svg").is_file()


def test_mutation_config_registers_suite_markers() -> None:
    config = mutmut_config(["tests_ai", "tests_independent"])

    assert '"independent: human-oracle and property-based verification tests"' in config
    assert 'pytest_add_cli_args_test_selection = ["tests_ai", "tests_independent"]' in config
