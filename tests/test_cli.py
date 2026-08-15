import runpy
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


def test_build_parser_exposes_reproduction_commands() -> None:
    aggregate = build_parser().parse_args(["aggregate-results", "--force"])
    independent = build_parser().parse_args(["check-independent", "--reference-only"])

    assert aggregate.command == "aggregate-results"
    assert aggregate.force is True
    assert independent.command == "check-independent"
    assert independent.reference_only is True


def test_main_validates_files(tmp_path: Path, capsys: object) -> None:
    create_empty_data_files(tmp_path)

    assert main(["validate-data", "--root", str(tmp_path)]) == 0
    assert "valid" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_main_reports_issues(tmp_path: Path, capsys: object) -> None:
    assert main(["validate-data", "--root", str(tmp_path)]) == 1
    assert "does not exist" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_module_entrypoint_delegates_to_cli(tmp_path: Path, monkeypatch: object) -> None:
    create_empty_data_files(tmp_path)
    monkeypatch.setattr("sys.argv", ["topic7", "validate-data", "--root", str(tmp_path)])  # type: ignore[attr-defined]
    try:
        runpy.run_module("topic7_experiment.__main__", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0


def test_reproduction_commands_delegate_to_scripts(monkeypatch: object) -> None:
    calls: list[list[str]] = []

    class Completed:
        returncode = 0

    def fake_run(command: list[str], check: bool) -> Completed:
        calls.append(command)
        assert check is False
        return Completed()

    monkeypatch.setattr("topic7_experiment.cli.subprocess.run", fake_run)
    assert main(["aggregate-results", "--force"]) == 0
    assert main(["check-independent", "--reference-only"]) == 0
    assert calls[0][-1] == "--force"
    assert calls[1][-1] == "--reference-only"
