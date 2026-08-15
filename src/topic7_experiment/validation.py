"""Validation for the experiment's manually collected CSV evidence."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

RUN_ID_PATTERN = re.compile(r"run-\d{2}")

METADATA_HEADERS = (
    "run_id",
    "tool",
    "model_displayed",
    "started_at",
    "ended_at",
    "context_clean",
    "clarification_asked",
    "ambiguities_detected",
    "followup_used",
    "human_edits",
    "raw_response_path",
    "transcript_path",
    "operator",
)

MEASUREMENT_HEADERS = (
    "run_id",
    "ai_tests_collected",
    "ai_tests_passed",
    "line_coverage",
    "branch_coverage",
    "acceptance_passed",
    "acceptance_total",
    "properties_failed",
    "mutants_total_ai",
    "killed_ai",
    "survived_ai",
    "timeout_ai",
    "error_ai",
    "equivalent_ai",
    "mutants_total_full",
    "killed_full",
    "survived_full",
    "timeout_full",
    "error_full",
    "equivalent_full",
    "raw_score_ai",
    "adjusted_score_ai",
    "raw_score_full",
    "adjusted_score_full",
)

COUNT_COLUMNS = {
    "ai_tests_collected",
    "ai_tests_passed",
    "acceptance_passed",
    "acceptance_total",
    "properties_failed",
    "mutants_total_ai",
    "killed_ai",
    "survived_ai",
    "timeout_ai",
    "error_ai",
    "equivalent_ai",
    "mutants_total_full",
    "killed_full",
    "survived_full",
    "timeout_full",
    "error_full",
    "equivalent_full",
}

PERCENTAGE_COLUMNS = {
    "line_coverage",
    "branch_coverage",
    "raw_score_ai",
    "adjusted_score_ai",
    "raw_score_full",
    "adjusted_score_full",
}


@dataclass(frozen=True, slots=True)
class CsvIssue:
    path: Path
    message: str
    row: int | None = None

    def __str__(self) -> str:
        location = f"{self.path}"
        if self.row is not None:
            location += f":row {self.row}"
        return f"{location}: {self.message}"


def _validate_number(
    path: Path,
    row_number: int,
    name: str,
    value: str,
    *,
    percentage_value: bool,
) -> CsvIssue | None:
    if value in {"", "NA"}:
        return None
    try:
        parsed = float(value) if percentage_value else int(value)
    except ValueError:
        expected_type = "a percentage" if percentage_value else "an integer"
        return CsvIssue(path, f"{name} must be {expected_type}, blank, or NA", row_number)
    upper_bound = 100 if percentage_value else None
    if parsed < 0 or (upper_bound is not None and parsed > upper_bound):
        expected = "between 0 and 100" if percentage_value else "non-negative"
        return CsvIssue(path, f"{name} must be {expected}", row_number)
    return None


def validate_csv(path: Path, expected_headers: tuple[str, ...]) -> list[CsvIssue]:
    """Validate one evidence CSV without changing it."""

    if not path.is_file():
        return [CsvIssue(path, "file does not exist")]

    issues: list[CsvIssue] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        actual_headers = tuple(reader.fieldnames or ())
        if actual_headers != expected_headers:
            return [
                CsvIssue(
                    path,
                    f"unexpected headers; expected {expected_headers}, got {actual_headers}",
                    1,
                )
            ]

        seen_run_ids: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            run_id = (row.get("run_id") or "").strip()
            if not RUN_ID_PATTERN.fullmatch(run_id):
                issues.append(CsvIssue(path, "run_id must match run-XX", row_number))
            elif run_id in seen_run_ids:
                issues.append(CsvIssue(path, f"duplicate run_id: {run_id}", row_number))
            else:
                seen_run_ids.add(run_id)

            for name in COUNT_COLUMNS.intersection(expected_headers):
                issue = _validate_number(
                    path,
                    row_number,
                    name,
                    (row.get(name) or "").strip(),
                    percentage_value=False,
                )
                if issue:
                    issues.append(issue)

            for name in PERCENTAGE_COLUMNS.intersection(expected_headers):
                issue = _validate_number(
                    path,
                    row_number,
                    name,
                    (row.get(name) or "").strip(),
                    percentage_value=True,
                )
                if issue:
                    issues.append(issue)

    return issues


def validate_default_data(root: Path) -> list[CsvIssue]:
    """Validate both canonical data files below a repository root."""

    return [
        *validate_csv(root / "experiments" / "metadata.csv", METADATA_HEADERS),
        *validate_csv(root / "results" / "measurements.csv", MEASUREMENT_HEADERS),
    ]
