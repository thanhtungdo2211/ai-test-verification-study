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
        {
            **base,
            "run_id": "bad",
            "ai_tests_collected": "x",
            "line_coverage": "101",
        },
        {**base, "run_id": "run-01", "acceptance_total": "-1"},
        {**base, "run_id": "run-01", "raw_score_ai": "not-a-score"},
        {**base, "run_id": "run-03", "branch_coverage": "nan"},
    ]
    write_csv(path, MEASUREMENT_HEADERS, rows)

    messages = [issue.message for issue in validate_csv(path, MEASUREMENT_HEADERS)]

    assert "run_id must match run-XX" in messages
    assert "ai_tests_collected must be an integer, blank, or NA" in messages
    assert "line_coverage must be between 0 and 100" in messages
    assert "acceptance_total must be non-negative" in messages
    assert "duplicate run_id: run-01" in messages
    assert "raw_score_ai must be a percentage, blank, or NA" in messages
    assert "branch_coverage must be between 0 and 100" in messages


def test_validate_default_data_checks_both_files(tmp_path: Path) -> None:
    write_csv(tmp_path / "experiments" / "metadata.csv", METADATA_HEADERS, [])
    write_csv(tmp_path / "results" / "measurements.csv", MEASUREMENT_HEADERS, [])

    assert validate_default_data(tmp_path) == []


def test_validate_metadata_row_contract(tmp_path: Path) -> None:
    path = tmp_path / "metadata.csv"
    row = dict.fromkeys(METADATA_HEADERS, "")
    row.update(
        {
            "run_id": "run-01",
            "tool": "test-tool",
            "model_displayed": "test-model",
            "operator": "tester",
            "context_clean": "yes",
            "clarification_asked": "no",
            "followup_used": "no",
            "ambiguities_detected": "2",
            "human_edits": "0",
            "started_at": "2026-08-15T08:00:00+00:00",
            "ended_at": "2026-08-15T08:01:00+00:00",
            "raw_response_path": "experiments/raw/run-01.txt",
            "transcript_path": "experiments/transcripts/run-01.md",
        }
    )
    write_csv(path, METADATA_HEADERS, [row])
    assert validate_csv(path, METADATA_HEADERS) == []


def test_validate_metadata_reports_protocol_fields(tmp_path: Path) -> None:
    path = tmp_path / "metadata.csv"
    row = dict.fromkeys(METADATA_HEADERS, "")
    row.update(
        {
            "run_id": "run-01",
            "context_clean": "sometimes",
            "ambiguities_detected": "not-a-count",
            "started_at": "tomorrow",
            "ended_at": "2026-08-15T08:00:00",
        }
    )
    write_csv(path, METADATA_HEADERS, [row])
    messages = [issue.message for issue in validate_csv(path, METADATA_HEADERS)]
    assert "context_clean must be yes, no, blank, or NA" in messages
    assert "ambiguities_detected must be an integer, blank, or NA" in messages
    assert "started_at must be an ISO-8601 timestamp" in messages
    assert "ended_at must include a timezone" in messages
    assert any(message.endswith("is required for a recorded run") for message in messages)


def test_validate_measurement_relationships_and_scores(tmp_path: Path) -> None:
    path = tmp_path / "measurements.csv"
    row = dict.fromkeys(MEASUREMENT_HEADERS, "")
    row.update(
        {
            "run_id": "run-01",
            "ai_tests_collected": "2",
            "ai_tests_passed": "3",
            "acceptance_total": "2",
            "acceptance_passed": "3",
            "mutants_total_ai": "10",
            "killed_ai": "5",
            "survived_ai": "2",
            "timeout_ai": "1",
            "error_ai": "1",
            "equivalent_ai": "2",
            "raw_score_ai": "99",
            "adjusted_score_ai": "99",
        }
    )
    invalid_equivalent = {**row, "run_id": "run-02", "equivalent_ai": "3"}
    write_csv(path, MEASUREMENT_HEADERS, [row, invalid_equivalent])
    messages = [issue.message for issue in validate_csv(path, MEASUREMENT_HEADERS)]
    assert "ai_tests_passed cannot exceed ai_tests_collected" in messages
    assert "acceptance_passed cannot exceed acceptance_total" in messages
    assert "equivalent_ai must be a subset of survived_ai" in messages
    assert "raw_score_ai does not match its mutant counts" in messages


def test_validate_default_data_requires_matching_run_ids(tmp_path: Path) -> None:
    metadata_row = dict.fromkeys(METADATA_HEADERS, "")
    metadata_row["run_id"] = "run-01"
    measurement_row = dict.fromkeys(MEASUREMENT_HEADERS, "")
    measurement_row["run_id"] = "run-02"
    write_csv(tmp_path / "experiments" / "metadata.csv", METADATA_HEADERS, [metadata_row])
    write_csv(tmp_path / "results" / "measurements.csv", MEASUREMENT_HEADERS, [measurement_row])

    messages = [issue.message for issue in validate_default_data(tmp_path)]
    assert "run_id missing from measurements: run-01" in messages
    assert "run_id missing from metadata: run-02" in messages
