"""Count and rank words from text or a command-line input file."""

import argparse
from collections import Counter
from collections.abc import Sequence
from contextlib import redirect_stderr, redirect_stdout
import io
import re
import sys
from typing import TextIO
import unicodedata


WORD_PATTERN = re.compile(r"[^\W_]+(?:'[^\W_]+)*")


def _normalise_word_characters(text: str) -> str:
    """Normalise apostrophes and separate anything but letters and decimal digits."""
    return "".join(
        character if (character == "'" or character.isdecimal()
                      or unicodedata.category(character).startswith("L")) else " "
        for character in text.lower().replace("’", "'")
    )


def count_words(text: str) -> list[tuple[str, int]]:
    """Return every word and count, ranked by frequency then alphabetically."""
    counts = Counter(WORD_PATTERN.findall(_normalise_word_characters(text)))
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))


def _read_text(path: str, stdin: TextIO | None) -> str:
    """Read UTF-8 input, replacing undecodable bytes at the input boundary."""
    if path == "-":
        source_input = sys.stdin if stdin is None else stdin
        if stdin is None and isinstance(source_input, io.TextIOWrapper):
            return source_input.buffer.read().decode("utf-8", errors="replace")
        return source_input.read()
    with open(path, encoding="utf-8", errors="replace") as source:
        return source.read()


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Print the most frequent words and return the command's exit code."""
    output: TextIO = sys.stdout if stdout is None else stdout
    error_output: TextIO = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(prog="wordfreq")
    parser.add_argument("file", help="UTF-8 input file, or - for stdin")
    parser.add_argument("--top", type=int, default=10, metavar="N",
                        help="show the top N words (default: 10)")
    with redirect_stderr(error_output), redirect_stdout(output):
        try:
            args = parser.parse_args(argv)
            if args.top < 1:
                parser.error("--top must be a positive integer")
        except SystemExit as error:
            return int(error.code or 0)
    if args.file == "-":
        text = _read_text(args.file, stdin)
    else:
        try:
            text = _read_text(args.file, stdin)
        except OSError as error:
            reason = " ".join(str(error.strerror or error).splitlines())
            error_output.write(f"wordfreq: error: {args.file}: {reason}\n")
            return 2
    for word, count in count_words(text)[:args.top]:
        output.write(f"{word} {count}\n")
    return 0
