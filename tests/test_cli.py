from pathlib import Path

from topic7_experiment.cli import build_parser, main
from topic7_experiment.validation import MEASUREMENT_HEADERS, METADATA_HEADERS


def create_empty_data_files(root: Path) -> None:
    metadata = root / "experiments" / "metadata.csv"
    measurements = root / "results" / "measurements.csv"
    metadata.parent.mkdir(parents=True)
    measurements.parent.mkdir(parents=True)
    metadata.write_text(",".join(METADATA_HEADERS) + "\n", encoding="utf-8")
    measurements.write_text(",".join(MEASUREMENT_HEADERS) + "\n", encoding="utf-8")


def test_build_parser_defaults_to_current_directory() -> None:
    args = build_parser().parse_args(["validate-data"])

    assert args.command == "validate-data"
    assert args.root == Path.cwd()


def test_main_validates_files(tmp_path: Path, capsys: object) -> None:
    create_empty_data_files(tmp_path)

    assert main(["validate-data", "--root", str(tmp_path)]) == 0
    assert "valid" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_main_reports_issues(tmp_path: Path, capsys: object) -> None:
    assert main(["validate-data", "--root", str(tmp_path)]) == 1
    assert "does not exist" in capsys.readouterr().out  # type: ignore[attr-defined]
