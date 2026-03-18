#!/usr/bin/env python3
"""CLI for counting lines, words, and characters in a text file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def existing_path(value: str) -> Path:
    """Validate that the CLI argument points to an existing file."""
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    return path


def count_text(text: str) -> tuple[int, int, int]:
    """Return line, word, and character counts for ``text``."""
    lines = len(text.splitlines())
    words = len(text.split())
    chars = len(text)
    return lines, words, chars


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count lines, words, and characters in a file.",
    )
    parser.add_argument("path", type=existing_path, help="Path to the file to count")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        parser.exit(1, f"Error reading {args.path}: {exc}\n")

    lines, words, chars = count_text(text)
    print(f"Lines: {lines}, Words: {words}, Chars: {chars}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
