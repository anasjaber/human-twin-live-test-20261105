# 03: Stdin input, argument validation and error handling

**What to build:** wordfreq behaves well in shell scripts. Passing `-` as the file reads all of stdin (UTF-8, undecodable bytes replaced) and works with `--top N`. Bad input is reported clearly with exit code 2 and nothing on stdout:
- Unreadable paths (missing file, directory, permission denied; any `OSError` while opening or reading) print one line `wordfreq: error: <path>: <reason>` to stderr and return 2.
- `--top` values that are zero, negative or not integers are argparse usage errors: usage message on stderr, exit 2.
- Running with no file argument is a usage error (exit 2). It never waits on stdin.

`--help` describes the file argument (including `-`) and `--top`. The README Usage section is extended to cover stdin and exit codes.

Tests use the `main` seam. For usage errors, keep argparse's output off the real terminal, either by routing parser output to the injected stderr or by redirecting `sys.stderr`. `main` may either return 2 or let `SystemExit(2)` propagate (see the spec's Testing Decisions).

**Blocked by:** 01 (Count and rank words in a file)

**Test location:** All tests live in `tests/test_wordfreq.py` (reviewer requirement).

**Status:** done

- [x] `python -m wordfreq -` reads stdin and prints the ranked `word count` lines, exit 0
- [x] `-` combined with `--top N` limits the output to N lines
- [x] Stdin is decoded as UTF-8 with undecodable bytes replaced (no crash on malformed input)
- [x] Missing file → stderr is exactly one line `wordfreq: error: <path>: <reason>`, stdout is empty, exit 2
- [x] A directory path and a permission-denied file are reported the same way (stderr line, empty stdout, exit 2)
- [x] `--top 0`, `--top -3` and `--top abc` → usage error on stderr, empty stdout, exit 2
- [x] No file argument → usage error on stderr, exit 2, no read from stdin
- [x] `--help` mentions the file argument (and `-` for stdin) and `--top` with its default of 10
- [x] Tests cover stdin via `-`, missing file, and invalid `--top` (0, negative, non-integer); the smoke test (or a second subprocess test) confirms the real process exit code is 2 for a missing file; `python -m unittest` passes
- [x] README Usage section shows reading stdin via `-` and states exit code 2 for missing files and usage errors
