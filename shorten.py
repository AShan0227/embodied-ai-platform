#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


DEFAULT_STORAGE_PATH = Path(__file__).with_name("urls.json")


class ShortenerError(Exception):
    """Base error for CLI failures."""


class InvalidURLError(ShortenerError):
    """Raised when a URL is not valid for shortening."""


class LookupError(ShortenerError):
    """Raised when a hash alias is not found."""


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InvalidURLError(f"Invalid URL: {url}")


def generate_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:6]


def load_mappings(storage_path: Path = DEFAULT_STORAGE_PATH) -> Dict[str, str]:
    if not storage_path.exists():
        return {}

    try:
        with storage_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ShortenerError(f"Failed to parse storage file: {storage_path}") from exc

    if not isinstance(data, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in data.items()
    ):
        raise ShortenerError(f"Storage file has invalid format: {storage_path}")

    return data


def save_mappings(mappings: Dict[str, str], storage_path: Path = DEFAULT_STORAGE_PATH) -> None:
    with storage_path.open("w", encoding="utf-8") as handle:
        json.dump(mappings, handle, indent=2, sort_keys=True)
        handle.write("\n")


def shorten_url(url: str, storage_path: Path = DEFAULT_STORAGE_PATH) -> str:
    validate_url(url)
    mappings = load_mappings(storage_path)

    for alias, existing_url in mappings.items():
        if existing_url == url:
            return alias

    alias = generate_hash(url)
    mappings[alias] = url
    save_mappings(mappings, storage_path)
    return alias


def lookup_url(alias: str, storage_path: Path = DEFAULT_STORAGE_PATH) -> str:
    mappings = load_mappings(storage_path)
    try:
        return mappings[alias]
    except KeyError as exc:
        raise LookupError(f"No URL found for hash: {alias}") from exc


def format_mappings(mappings: Dict[str, str]) -> str:
    if not mappings:
        return "No URL mappings stored."
    return "\n".join(f"{alias} {url}" for alias, url in sorted(mappings.items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate short aliases for URLs.")
    parser.add_argument("url", nargs="?", help="The URL to shorten.")
    parser.add_argument("--lookup", metavar="HASH", help="Retrieve the original URL for a hash.")
    parser.add_argument("--list", action="store_true", dest="list_mappings", help="List all stored mappings.")
    parser.add_argument(
        "--storage",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help="Path to the JSON storage file.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    actions_requested = sum([bool(args.url), bool(args.lookup), bool(args.list_mappings)])
    if actions_requested != 1:
        parser.error("provide exactly one of: URL argument, --lookup, or --list")

    try:
        if args.url:
            print(shorten_url(args.url, args.storage))
        elif args.lookup:
            print(lookup_url(args.lookup, args.storage))
        else:
            print(format_mappings(load_mappings(args.storage)))
    except ShortenerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
