"""Command line entry point.

Run with: uv run wordcount FILE
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from wordcount_cli.wordcount import top_words


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wordcount",
        description="Show the most common words in a text file.",
    )
    parser.add_argument("file", help="text file to read. '-' reads stdin")
    parser.add_argument(
        "-n",
        "--limit",
        type=_positive_int,
        default=10,
        help="how many words to show (default: 10)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command. The return value is the exit code."""
    args = build_parser().parse_args(argv)
    file: str = args.file
    limit: int = args.limit

    try:
        text = sys.stdin.read() if file == "-" else Path(file).read_text("utf-8")
    except OSError as e:
        print(f"wordcount: {e}", file=sys.stderr)
        return 1

    for word, count in top_words(text, limit):
        print(f"{count:>6}  {word}")
    return 0


if __name__ == "__main__":
    # Run with: uv run python -m wordcount_cli.cli FILE
    # A debugger can start the program this way.
    sys.exit(main())
