from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("fibonacci.py")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_basic_output_fib_1() -> None:
    result = run_cli("1")
    assert result.returncode == 0
    assert result.stdout.strip() == "0"


def test_basic_output_fib_5() -> None:
    result = run_cli("5")
    assert result.returncode == 0
    assert result.stdout.strip() == "0 1 1 2 3"


def test_basic_output_fib_10() -> None:
    result = run_cli("10")
    assert result.returncode == 0
    assert result.stdout.strip() == "0 1 1 2 3 5 8 13 21 34"


def test_rejects_zero() -> None:
    result = run_cli("0")
    assert result.returncode != 0
    assert "N must be a positive integer" in result.stderr


def test_accepts_one() -> None:
    result = run_cli("1")
    assert result.returncode == 0
    assert result.stdout.strip() == "0"


def test_rejects_negative_numbers() -> None:
    result = run_cli("-3")
    assert result.returncode != 0
    assert "N must be a positive integer" in result.stderr


def test_json_flag_outputs_json_array() -> None:
    result = run_cli("5", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == [0, 1, 1, 2, 3]
