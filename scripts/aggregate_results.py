#!/usr/bin/env python3
"""Rebuild measurements and lightweight SVG figures from raw evidence.

The aggregator is intentionally deterministic and dependency-free.  It reads
metadata, baseline manifests/JUnit reports, and mutation manifests; it never
edits transcripts, candidates, or raw logs.  Missing evidence stays blank in
the generated CSV and is rendered as ``NA`` in figures.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.run_tests import parse_coverage
from topic7_experiment.metrics import MutationCounts
from topic7_experiment.validation import MEASUREMENT_HEADERS

ROOT = Path(__file__).resolve().parents[1]
RUN_ID_PATTERN = re.compile(r"run-\d{2}")


@dataclass(frozen=True, slots=True)
class MutationEvidence:
    killed: int | None = None
    survived: int | None = None
    timeout: int | None = None
    error: int | None = None
    equivalent: int | None = None
    total: int | None = None

    def counts(self) -> MutationCounts | None:
        values = (self.killed, self.survived, self.timeout, self.error)
        if any(value is None for value in values):
            return None
        return MutationCounts(
            killed=self.killed or 0,
            survived=self.survived or 0,
            timeout=self.timeout or 0,
            error=self.error or 0,
            equivalent=self.equivalent or 0,
        )


def _int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _first_int(data: dict[str, Any], names: Iterable[str]) -> int | None:
    for name in names:
        value = _int(data.get(name))
        if value is not None:
            return value
    return None


def _error_count(data: dict[str, Any]) -> int | None:
    explicit = _first_int(data, ("error", "errors", "error_mutants"))
    if explicit is not None:
        return explicit
    status_names = (
        "no_tests",
        "skipped",
        "suspicious",
        "check_was_interrupted_by_user",
        "segfault",
        "caught_by_type_check",
    )
    values = [_int(data.get(name)) for name in status_names]
    if all(value is None for value in values):
        return None
    return sum(value or 0 for value in values)


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def parse_mutation_evidence(directory: Path) -> MutationEvidence:
    """Parse a wrapper manifest or mutmut stats without guessing missing data."""

    manifest = read_json(directory / "manifest.json")
    candidates = [manifest, read_json(directory / "mutmut-cicd-stats.json")]
    for data in candidates:
        if not data:
            continue
        nested = data.get("counts") if isinstance(data.get("counts"), dict) else data
        evidence = MutationEvidence(
            killed=_first_int(nested, ("killed", "killed_mutants", "tests_killed")),
            survived=_first_int(nested, ("survived", "surviving", "survived_mutants")),
            timeout=_first_int(nested, ("timeout", "timeouts", "timeout_mutants")),
            error=_error_count(nested),
            equivalent=_first_int(nested, ("equivalent", "equivalent_mutants")),
            total=_first_int(nested, ("total", "total_generated", "mutants_total")),
        )
        if any(value is not None for value in (evidence.killed, evidence.survived, evidence.total)):
            return evidence
    return MutationEvidence()


def _junit_cases(path: Path) -> list[ET.Element]:
    if not path.is_file():
        return []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return []
    return list(root.iter("testcase"))


def _case_failed(case: ET.Element) -> bool:
    return any(case.find(tag) is not None for tag in ("failure", "error"))


def _case_skipped(case: ET.Element) -> bool:
    return case.find("skipped") is not None


def acceptance_counts(path: Path) -> tuple[int | None, int | None, int | None]:
    """Return passed, total, and failed property counts from JUnit XML."""

    cases = [
        case
        for case in _junit_cases(path)
        if "acceptance" in (case.attrib.get("name", "") + case.attrib.get("classname", "")).lower()
        and not case.attrib.get("name", "").lower().startswith("test_reference_")
    ]
    if not cases:
        return None, None, None
    passed = sum(not _case_failed(case) and not _case_skipped(case) for case in cases)
    property_cases = [
        case
        for case in _junit_cases(path)
        if "propert" in (case.attrib.get("name", "") + case.attrib.get("classname", "")).lower()
    ]
    properties_failed = sum(_case_failed(case) for case in property_cases)
    return passed, len(cases), properties_failed


def _manifest(directory: Path) -> dict[str, Any]:
    return read_json(directory / "manifest.json")


def _find_baseline(root: Path, run_id: str, suite: str) -> Path:
    nested = root / "results" / "baseline" / run_id / suite
    if nested.is_dir():
        return nested
    legacy = root / "results" / "baseline" / run_id
    return legacy if suite == "ai-only" else nested


def _number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _float_or_none(value: Any) -> float | None:
    if value in {None, "", "NA"}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _mutation_fields(evidence: MutationEvidence) -> dict[str, Any]:
    counts = evidence.counts()
    if counts is None:
        return {
            "total": None,
            "killed": None,
            "survived": None,
            "timeout": None,
            "error": None,
            "equivalent": None,
            "raw": None,
            "adjusted": None,
        }
    adjusted = counts.adjusted_score if evidence.equivalent is not None else None
    return {
        "total": evidence.total if evidence.total is not None else counts.total_generated,
        "killed": counts.killed,
        "survived": counts.survived,
        "timeout": counts.timeout,
        "error": counts.error,
        "equivalent": evidence.equivalent,
        "raw": counts.raw_score,
        "adjusted": adjusted,
    }


def measurement_row(root: Path, metadata: dict[str, str]) -> dict[str, str]:
    run_id = metadata["run_id"]
    ai_dir = _find_baseline(root, run_id, "ai-only")
    full_dir = _find_baseline(root, run_id, "full")
    independent_dir = _find_baseline(root, run_id, "independent")
    ai_manifest = _manifest(ai_dir)
    full_manifest = _manifest(full_dir)
    independent_manifest = _manifest(independent_dir)
    coverage_manifest = full_manifest or independent_manifest or ai_manifest
    coverage_dir = (
        full_dir if full_manifest else independent_dir if independent_manifest else ai_dir
    )
    coverage_report = parse_coverage(coverage_dir / "coverage.json")
    acceptance_dir = full_dir if (full_dir / "junit.xml").is_file() else independent_dir
    acceptance_passed, acceptance_total, properties_failed = acceptance_counts(
        acceptance_dir / "junit.xml"
    )
    ai_mutation = _mutation_fields(
        parse_mutation_evidence(root / "results" / "mutation-ai-only" / run_id)
    )
    full_mutation = _mutation_fields(
        parse_mutation_evidence(root / "results" / "mutation-independent" / run_id)
    )
    values: dict[str, Any] = {
        "run_id": run_id,
        "ai_tests_collected": ai_manifest.get("collected"),
        "ai_tests_passed": ai_manifest.get("passed"),
        "line_coverage": coverage_manifest.get("line_coverage") or coverage_report["line_coverage"],
        "branch_coverage": coverage_manifest.get("branch_coverage")
        or coverage_report["branch_coverage"],
        "acceptance_passed": acceptance_passed,
        "acceptance_total": acceptance_total,
        "properties_failed": properties_failed,
        "mutants_total_ai": ai_mutation["total"],
        "killed_ai": ai_mutation["killed"],
        "survived_ai": ai_mutation["survived"],
        "timeout_ai": ai_mutation["timeout"],
        "error_ai": ai_mutation["error"],
        "equivalent_ai": ai_mutation["equivalent"],
        "mutants_total_full": full_mutation["total"],
        "killed_full": full_mutation["killed"],
        "survived_full": full_mutation["survived"],
        "timeout_full": full_mutation["timeout"],
        "error_full": full_mutation["error"],
        "equivalent_full": full_mutation["equivalent"],
        "raw_score_ai": ai_mutation["raw"],
        "adjusted_score_ai": ai_mutation["adjusted"],
        "raw_score_full": full_mutation["raw"],
        "adjusted_score_full": full_mutation["adjusted"],
    }
    return {name: _number(values.get(name)) for name in MEASUREMENT_HEADERS}  # type: ignore[arg-type]


def read_metadata(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_measurements(path: Path, rows: list[dict[str, str]], *, force: bool) -> None:
    if path.exists() and path.stat().st_size > 0 and not force:
        raise FileExistsError(f"refusing to overwrite {path}; pass --force for generated data")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MEASUREMENT_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _svg_bar_chart(
    path: Path, title: str, values: list[tuple[str, float | None]], *, maximum: float = 100.0
) -> None:
    width, height = 960, 440
    usable_width = width - 80
    baseline = height - 70
    available_height = baseline - 70
    bars = max(1, len(values))
    bar_width = max(8, usable_width // bars - 10)
    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        "<style>text{font-family: sans-serif; fill: #222} .muted{fill:#777}</style>",
        f'<text x="40" y="35" font-size="22">{title}</text>',
        f'<line x1="40" y1="{baseline}" x2="{width - 20}" y2="{baseline}" stroke="#333"/>',
    ]
    if not values:
        lines.append('<text class="muted" x="40" y="150" font-size="18">No data available</text>')
    for index, (label, raw_value) in enumerate(values):
        x = 50 + index * (usable_width // bars)
        value = max(0.0, min(maximum, raw_value or 0.0))
        bar_height = available_height * value / maximum if maximum else 0
        y = baseline - bar_height
        color = "#4472c4" if raw_value is not None else "#bbb"
        lines.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
            f'height="{bar_height:.1f}" fill="{color}"/>'
        )
        display = "NA" if raw_value is None else f"{raw_value:.2f}".rstrip("0").rstrip(".")
        lines.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{max(60, y - 6):.1f}" '
            f'font-size="11" text-anchor="middle">{display}</text>'
        )
        lines.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{baseline + 18}" '
            f'font-size="10" text-anchor="middle">{label}</text>'
        )
    lines.append("</svg>\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_figures(root: Path, rows: list[dict[str, str]]) -> None:
    output = root / "results" / "figures"
    output.mkdir(parents=True, exist_ok=True)
    labels = [row["run_id"] for row in rows]

    def values(name: str) -> list[tuple[str, float | None]]:
        return [
            (label, _float_or_none(row.get(name))) for label, row in zip(labels, rows, strict=True)
        ]

    _svg_bar_chart(
        output / "mutation-scores.svg", "Mutation score — AI-only", values("raw_score_ai")
    )
    _svg_bar_chart(output / "coverage-acceptance.svg", "Line coverage", values("line_coverage"))
    _svg_bar_chart(
        output / "property-failures.svg",
        "Property failures",
        values("properties_failed"),
        maximum=max(
            [
                _float_or_none(row.get("properties_failed"))
                for row in rows
                if _float_or_none(row.get("properties_failed")) is not None
            ]
            or [1]
        ),
    )
    _svg_bar_chart(
        output / "mutation-survivors.svg",
        "Surviving mutants — full suite",
        values("survived_full"),
        maximum=max(
            [
                _float_or_none(row.get("survived_full"))
                for row in rows
                if _float_or_none(row.get("survived_full")) is not None
            ]
            or [1]
        ),
    )
    _svg_bar_chart(
        output / "acceptance-score.svg",
        "Acceptance pass rate",
        [
            (
                label,
                (
                    _float_or_none(row.get("acceptance_passed"))
                    / _float_or_none(row.get("acceptance_total"))
                    * 100
                )
                if _float_or_none(row.get("acceptance_passed")) is not None
                and _float_or_none(row.get("acceptance_total")) not in {None, 0}
                else None,
            )
            for label, row in zip(labels, rows, strict=True)
        ],
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--force", action="store_true", help="replace generated measurements.csv")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    rows = [
        measurement_row(root, metadata)
        for metadata in read_metadata(root / "experiments" / "metadata.csv")
    ]
    try:
        write_measurements(root / "results" / "measurements.csv", rows, force=args.force)
    except FileExistsError as exc:
        print(exc)
        return 2
    generate_figures(root, rows)
    print(f"Generated {len(rows)} measurement row(s) and figures under {root / 'results'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
