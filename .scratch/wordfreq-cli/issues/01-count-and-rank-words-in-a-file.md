# 01: Count and rank words in a file (tracer bullet)

**What to build:** A user in a checkout can run `python -m wordfreq FILE` (optionally with `--top N`) and get the most frequent **words** in that file, one per line as `word count`, most frequent first, ties alphabetical, default **top N** of 10. This ticket sets up the whole path end to end: the `wordfreq` package runnable with `python -m wordfreq`, the CLI entry point `main(argv=None, stdin=None, stdout=None, stderr=None) -> int` (streams default to `sys.stdin`/`sys.stdout`/`sys.stderr`; `__main__` calls `sys.exit(main())`), a pure counting function returning the full ranked `(word, count)` list, the `unittest` test package at the repo root, the one `subprocess` smoke test, and a first README "Usage" section.

For this ticket a **word** only needs the basic rule: lowercase the text, then split on anything that isn't a Unicode letter or digit (whitespace, newlines, tabs, commas, full stops, quotes, brackets). The full rule (apostrophes in contractions, typographic `’`, hyphen splits, underscore, non-ASCII and digit edge cases) is ticket 02. `--top` validation, stdin via `-` and file errors are ticket 03.

Python 3.10+ standard library only; no packaging metadata. Tests go through the `main(argv, stdin, stdout, stderr)` seam with `io.StringIO` streams and `tempfile` input files, asserting only stdout/stderr and the returned exit code (see the spec's Testing Decisions).

**Blocked by:** None (can start immediately)

**Test location:** All tests live in `tests/test_wordfreq.py` (reviewer requirement).

**Status:** done

- [x] `python -m wordfreq FILE` prints up to 10 lines of `word count` (single space, newline-terminated, no header or summary) and exits 0
- [x] `--top N` with a positive integer prints at most N lines
- [x] Fewer distinct words than N → only those lines are printed, exit 0
- [x] Ordering is count descending, then word ascending (plain Python string order)
- [x] "The", "the" and "THE" count as one word and print as `the`
- [x] Words split on any whitespace (spaces, tabs, newlines) and common punctuation (commas, full stops, quotes, brackets), so `word,` and `word` count together
- [x] Empty file, or one with only punctuation/whitespace → no output, exit 0
- [x] Files are read as UTF-8 with `errors="replace"`
- [x] Only the Python standard library is used
- [x] `python -m unittest` from the repo root discovers and passes the tests (a `tests` package with `test_*.py` modules)
- [x] In-process tests cover: default top 10, `--top N`, fewer than N, alphabetical tie-break, case-insensitivity, punctuation ignored, empty input
- [x] One smoke test runs `python -m wordfreq` via `subprocess` with `sys.executable` on a temp file and checks stdout and exit code 0
- [x] README has a "Usage" section showing `python -m wordfreq FILE`, `--top N`, the `word count` output format, and how to run the tests
