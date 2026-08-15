import csv
from pathlib import Path

from topic7_experiment.validation import (
    MEASUREMENT_HEADERS,
    METADATA_HEADERS,
    CsvIssue,
    validate_csv,
    validate_default_data,
)


def write_csv(path: Path, headers: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def test_csv_issue_formats_optional_row(tmp_path: Path) -> None:
    assert str(CsvIssue(tmp_path / "data.csv", "bad")).endswith("data.csv: bad")
    assert str(CsvIssue(tmp_path / "data.csv", "bad", 2)).endswith("data.csv:row 2: bad")


def test_validate_csv_accepts_empty_template(tmp_path: Path) -> None:
    path = tmp_path / "metadata.csv"
    write_csv(path, METADATA_HEADERS, [])

    assert validate_csv(path, METADATA_HEADERS) == []


def test_validate_csv_reports_missing_file(tmp_path: Path) -> None:
    issues = validate_csv(tmp_path / "missing.csv", METADATA_HEADERS)

    assert len(issues) == 1
    assert "does not exist" in str(issues[0])


def test_validate_csv_reports_header_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "metadata.csv"
    write_csv(path, ("wrong",), [])

    issues = validate_csv(path, METADATA_HEADERS)

    assert len(issues) == 1
    assert "unexpected headers" in str(issues[0])


def test_validate_measurements_reports_bad_rows(tmp_path: Path) -> None:
    path = tmp_path / "measurements.csv"
    base = dict.fromkeys(MEASUREMENT_HEADERS, "")
    rows = [
        {**base, "run_id": "bad", "ai_tests_collected": "x", "line_coverage": "101"},
        {**base, "run_id": "run-01", "acceptance_total": "-1"},
        {**base, "run_id": "run-01", "raw_score_ai": "not-a-score"},
    ]
    write_csv(path, MEASUREMENT_HEADERS, rows)

    messages = [issue.message for issue in validate_csv(path, MEASUREMENT_HEADERS)]

    assert "run_id must match run-XX" in messages
    assert "ai_tests_collected must be an integer, blank, or NA" in messages
    assert "line_coverage must be between 0 and 100" in messages
    assert "acceptance_total must be non-negative" in messages
    assert "duplicate run_id: run-01" in messages
    assert "raw_score_ai must be a percentage, blank, or NA" in messages


def test_validate_default_data_checks_both_files(tmp_path: Path) -> None:
    write_csv(tmp_path / "experiments" / "metadata.csv", METADATA_HEADERS, [])
    write_csv(tmp_path / "results" / "measurements.csv", MEASUREMENT_HEADERS, [])

    assert validate_default_data(tmp_path) == []
