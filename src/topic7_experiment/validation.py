"""Validation for the experiment's manually collected CSV evidence."""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from topic7_experiment.metrics import MutationCounts

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

BOOLEAN_COLUMNS = {"context_clean", "clarification_asked", "followup_used"}
METADATA_COUNT_COLUMNS = {"ambiguities_detected", "human_edits"}
PATH_COLUMNS = {"raw_response_path", "transcript_path"}
REQUIRED_METADATA_COLUMNS = {"tool", "model_displayed", "started_at", "ended_at", "operator"}


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
    if (
        not math.isfinite(parsed)
        or parsed < 0
        or (upper_bound is not None and parsed > upper_bound)
    ):
        expected = "between 0 and 100" if percentage_value else "non-negative"
        return CsvIssue(path, f"{name} must be {expected}", row_number)
    return None


def _validate_metadata_row(path: Path, row_number: int, row: dict[str, str]) -> list[CsvIssue]:
    issues: list[CsvIssue] = []
    for name in REQUIRED_METADATA_COLUMNS:
        value = (row.get(name) or "").strip()
        if value in {"", "NA"}:
            issues.append(CsvIssue(path, f"{name} is required for a recorded run", row_number))
    for name in BOOLEAN_COLUMNS:
        value = (row.get(name) or "").strip().lower()
        if value not in {"", "na", "yes", "no"}:
            issues.append(CsvIssue(path, f"{name} must be yes, no, blank, or NA", row_number))

    for name in METADATA_COUNT_COLUMNS:
        issue = _validate_number(
            path,
            row_number,
            name,
            (row.get(name) or "").strip(),
            percentage_value=False,
        )
        if issue:
            issues.append(issue)

    timestamps: dict[str, datetime] = {}
    for name in ("started_at", "ended_at"):
        value = (row.get(name) or "").strip()
        if value in {"", "NA"}:
            continue
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            issues.append(CsvIssue(path, f"{name} must be an ISO-8601 timestamp", row_number))
            continue
        if parsed.tzinfo is None:
            issues.append(CsvIssue(path, f"{name} must include a timezone", row_number))
        timestamps[name] = parsed
    if "started_at" in timestamps and "ended_at" in timestamps:
        if timestamps["ended_at"] < timestamps["started_at"]:
            issues.append(CsvIssue(path, "ended_at cannot precede started_at", row_number))

    for name in PATH_COLUMNS:
        value = (row.get(name) or "").strip()
        if value == "":
            issues.append(CsvIssue(path, f"{name} is required for a recorded run", row_number))
    return issues


def _validate_measurement_relationships(
    path: Path, row_number: int, row: dict[str, str]
) -> list[CsvIssue]:
    issues: list[CsvIssue] = []

    def integer(name: str) -> int | None:
        value = (row.get(name) or "").strip()
        if value in {"", "NA"}:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    ai_collected, ai_passed = integer("ai_tests_collected"), integer("ai_tests_passed")
    if ai_collected is not None and ai_passed is not None and ai_passed > ai_collected:
        issues.append(
            CsvIssue(path, "ai_tests_passed cannot exceed ai_tests_collected", row_number)
        )
    acceptance_total, acceptance_passed = integer("acceptance_total"), integer("acceptance_passed")
    if (
        acceptance_total is not None
        and acceptance_passed is not None
        and acceptance_passed > acceptance_total
    ):
        issues.append(
            CsvIssue(path, "acceptance_passed cannot exceed acceptance_total", row_number)
        )

    for prefix in ("ai", "full"):
        names = {
            "killed": f"killed_{prefix}",
            "survived": f"survived_{prefix}",
            "timeout": f"timeout_{prefix}",
            "error": f"error_{prefix}",
            "equivalent": f"equivalent_{prefix}",
            "total": f"mutants_total_{prefix}",
        }
        values = {key: integer(name) for key, name in names.items()}
        if any(value is None for value in values.values()):
            continue
        if any(value < 0 for value in values.values() if value is not None):
            continue
        if (values["equivalent"] or 0) > (values["survived"] or 0):
            issues.append(
                CsvIssue(
                    path,
                    f"equivalent_{prefix} must be a subset of survived_{prefix}",
                    row_number,
                )
            )
            continue
        counts = MutationCounts(
            killed=values["killed"] or 0,
            survived=values["survived"] or 0,
            timeout=values["timeout"] or 0,
            error=values["error"] or 0,
            equivalent=values["equivalent"] or 0,
        )
        if counts.total_generated != values["total"]:
            issues.append(
                CsvIssue(
                    path,
                    f"mutants_total_{prefix} must equal killed + survived + timeout + error",
                    row_number,
                )
            )
        for score_name, expected in (
            (f"raw_score_{prefix}", counts.raw_score),
            (f"adjusted_score_{prefix}", counts.adjusted_score),
        ):
            actual_text = (row.get(score_name) or "").strip()
            if expected is None or actual_text in {"", "NA"}:
                continue
            try:
                actual = float(actual_text)
            except ValueError:
                continue  # _validate_number emits the type error.
            if abs(actual - expected) > 0.01:
                issues.append(
                    CsvIssue(path, f"{score_name} does not match its mutant counts", row_number)
                )
    return issues


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

            if expected_headers == METADATA_HEADERS:
                issues.extend(_validate_metadata_row(path, row_number, row))
            elif expected_headers == MEASUREMENT_HEADERS:
                issues.extend(_validate_measurement_relationships(path, row_number, row))

    return issues


def validate_default_data(root: Path) -> list[CsvIssue]:
    """Validate both canonical data files below a repository root."""

    metadata_path = root / "experiments" / "metadata.csv"
    measurements_path = root / "results" / "measurements.csv"
    issues = [
        *validate_csv(metadata_path, METADATA_HEADERS),
        *validate_csv(measurements_path, MEASUREMENT_HEADERS),
    ]
    if metadata_path.is_file() and measurements_path.is_file():
        with metadata_path.open(encoding="utf-8", newline="") as handle:
            metadata_ids = {
                row.get("run_id", "").strip()
                for row in csv.DictReader(handle)
                if row.get("run_id", "").strip()
            }
        with measurements_path.open(encoding="utf-8", newline="") as handle:
            measurement_ids = {
                row.get("run_id", "").strip()
                for row in csv.DictReader(handle)
                if row.get("run_id", "").strip()
            }
        for run_id in sorted(metadata_ids - measurement_ids):
            issues.append(
                CsvIssue(measurements_path, f"run_id missing from measurements: {run_id}")
            )
        for run_id in sorted(measurement_ids - metadata_ids):
            issues.append(CsvIssue(metadata_path, f"run_id missing from metadata: {run_id}"))
    return issues
