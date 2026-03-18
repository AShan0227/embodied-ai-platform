#!/usr/bin/env python3
"""CLI for checking HTTP HEAD responses for markdown links."""

from __future__ import annotations

import argparse
import os
import socket
import sys
from pathlib import Path
from urllib import error, request


MARKDOWN_LINK_RE = (
    r"\[[^\]]+\]\(<([^>\s]+)>\)"
    r"|"
    r"\[[^\]]+\]\(([^)\s]+)\)"
)

STATUS_OK = "✅ OK"
STATUS_BROKEN = "❌ BROKEN"
STATUS_TIMEOUT = "⚠️ TIMEOUT"


def existing_path(value: str) -> Path:
    """Validate that the CLI argument points to an existing file."""
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    return path


def extract_urls(markdown: str) -> list[str]:
    """Return URLs from markdown links."""
    import re

    matches = re.findall(MARKDOWN_LINK_RE, markdown)
    return [angle or plain for angle, plain in matches]


def request_timeout() -> float:
    """Return the HEAD request timeout in seconds."""
    raw_value = os.environ.get("LINKCHECK_TIMEOUT", "5")
    try:
        return float(raw_value)
    except ValueError:
        return 5.0


def classify_url(url: str, timeout: float) -> str:
    """Check a URL with HEAD and return the display status."""
    req = request.Request(url, method="HEAD")
    try:
        with request.urlopen(req, timeout=timeout):
            return STATUS_OK
    except error.HTTPError:
        return STATUS_BROKEN
    except error.URLError as exc:
        if isinstance(exc.reason, socket.timeout):
            return STATUS_TIMEOUT
        return STATUS_BROKEN
    except socket.timeout:
        return STATUS_TIMEOUT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check markdown links with HTTP HEAD requests.",
    )
    parser.add_argument("path", type=existing_path, help="Path to the markdown file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        markdown = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        parser.exit(1, f"Error reading {args.path}: {exc}\n")

    timeout = request_timeout()
    has_broken = False

    for url in extract_urls(markdown):
        status = classify_url(url, timeout)
        print(f"{status} {url}")
        if status == STATUS_BROKEN:
            has_broken = True

    return 1 if has_broken else 0


if __name__ == "__main__":
    sys.exit(main())
