import json
from pathlib import Path
import subprocess
import sys

import pytest

import shorten


def test_hash_generation_is_deterministic() -> None:
    url = "https://example.com/very/long/path"
    assert shorten.generate_hash(url) == shorten.generate_hash(url)
    assert len(shorten.generate_hash(url)) == 6


def test_duplicate_url_handling(tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"
    url = "https://example.com/very/long/path"

    first = shorten.shorten_url(url, storage)
    second = shorten.shorten_url(url, storage)

    assert first == second
    assert json.loads(storage.read_text(encoding="utf-8")) == {first: url}


def test_lookup_by_hash(tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"
    url = "https://example.com/docs/page"
    alias = shorten.shorten_url(url, storage)

    assert shorten.lookup_url(alias, storage) == url


def test_list_all_mappings(tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"
    first_url = "https://example.com/a"
    second_url = "https://example.com/b"
    first_alias = shorten.shorten_url(first_url, storage)
    second_alias = shorten.shorten_url(second_url, storage)

    output = shorten.format_mappings(shorten.load_mappings(storage))

    assert output == "\n".join(
        f"{alias} {url}"
        for alias, url in sorted(
            [(first_alias, first_url), (second_alias, second_url)],
            key=lambda item: item[0],
        )
    )


@pytest.mark.parametrize(
    "invalid_url",
    [
        "example.com/no-scheme",
        "ftp://example.com/resource",
        "https:///missing-host",
    ],
)
def test_invalid_url_handling(invalid_url: str, tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"

    with pytest.raises(shorten.InvalidURLError):
        shorten.shorten_url(invalid_url, storage)


def test_cli_lookup_and_list(tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"
    url = "https://example.com/e2e"

    shorten_result = subprocess.run(
        [sys.executable, "shorten.py", url, "--storage", str(storage)],
        capture_output=True,
        text=True,
        check=True,
    )
    alias = shorten_result.stdout.strip()

    lookup_result = subprocess.run(
        [sys.executable, "shorten.py", "--lookup", alias, "--storage", str(storage)],
        capture_output=True,
        text=True,
        check=True,
    )
    list_result = subprocess.run(
        [sys.executable, "shorten.py", "--list", "--storage", str(storage)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert lookup_result.stdout.strip() == url
    assert list_result.stdout.strip() == f"{alias} {url}"


def test_cli_invalid_url_exits_with_error(tmp_path: Path) -> None:
    storage = tmp_path / "urls.json"

    result = subprocess.run(
        [sys.executable, "shorten.py", "not-a-url", "--storage", str(storage)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Invalid URL" in result.stderr
