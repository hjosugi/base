import io
from pathlib import Path

import pytest

from pythonbase.cli import main


@pytest.fixture
def text_file(tmp_path: Path) -> Path:
    path = tmp_path / "words.txt"
    path.write_text("one two two three three three", encoding="utf-8")
    return path


def test_prints_counts(text_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(text_file)]) == 0

    assert capsys.readouterr().out.splitlines() == [
        "     3  three",
        "     2  two",
        "     1  one",
    ]


def test_limit_option(text_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(text_file), "-n", "1"]) == 0

    assert capsys.readouterr().out == "     3  three\n"


def test_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("x x"))

    assert main(["-"]) == 0

    assert capsys.readouterr().out == "     2  x\n"


def test_missing_file_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(tmp_path / "missing.txt")]) == 1

    assert "missing.txt" in capsys.readouterr().err


def test_bad_limit_is_a_usage_error(text_file: Path) -> None:
    # argparse exits with code 2 for a usage error.
    with pytest.raises(SystemExit) as excinfo:
        main([str(text_file), "-n", "0"])

    assert excinfo.value.code == 2
