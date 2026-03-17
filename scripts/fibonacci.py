#!/usr/bin/env python3
"""CLI for printing the first N Fibonacci numbers."""

from __future__ import annotations

import argparse
import json
import sys


def positive_int(value: str) -> int:
    """Validate that a CLI argument is a positive integer."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("N must be a positive integer") from exc

    if parsed <= 0:
        raise argparse.ArgumentTypeError("N must be a positive integer")

    return parsed


def fibonacci_numbers(count: int) -> list[int]:
    """Return the first ``count`` Fibonacci numbers."""
    numbers: list[int] = []
    current, nxt = 0, 1
    for _ in range(count):
        numbers.append(current)
        current, nxt = nxt, current + nxt
    return numbers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print the first N Fibonacci numbers.",
    )
    parser.add_argument("n", type=positive_int, help="Number of Fibonacci values to print")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print the sequence as JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sequence = fibonacci_numbers(args.n)

    if args.json_output:
        print(json.dumps(sequence))
    else:
        print(" ".join(str(number) for number in sequence))

    return 0


if __name__ == "__main__":
    sys.exit(main())
