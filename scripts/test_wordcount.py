from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("wordcount.py")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_counts_lines_words_and_chars(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("hello world\nsecond line\n", encoding="utf-8")

    result = run_cli(str(sample))

    assert result.returncode == 0
    assert result.stdout.strip() == "Lines: 2, Words: 4, Chars: 24"


def test_counts_single_line_without_trailing_newline(tmp_path: Path) -> None:
    sample = tmp_path / "single-line.txt"
    sample.write_text("one two three", encoding="utf-8")

    result = run_cli(str(sample))

    assert result.returncode == 0
    assert result.stdout.strip() == "Lines: 1, Words: 3, Chars: 13"


def test_rejects_missing_file() -> None:
    result = run_cli("missing.txt")

    assert result.returncode != 0
    assert "File not found: missing.txt" in result.stderr
