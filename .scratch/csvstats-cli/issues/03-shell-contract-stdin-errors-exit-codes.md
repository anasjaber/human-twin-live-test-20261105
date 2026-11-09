# 03: Shell contract: stdin, input errors and exit codes

**What to build:** The tool behaves well in shell pipelines and scripts:

- `python -m csvstats -` reads the CSV from stdin (the given text stream, as is).
- When the input can't be opened or read (missing file, a directory, permission denied, invalid UTF-8, or a `csv.Error` during parsing), the tool writes `csvstats: error: <file>: <reason>` to stderr, writes nothing to stdout, and returns exit code 2.
- No argument or two arguments give argparse's usage message on stderr and exit 2. `--help` explains the `file` argument (including `-`) and exits 0. Let argparse raise `SystemExit` for these rather than overriding it.
- Summary on stdout, errors on stderr, exit 0 on success.
- One subprocess smoke test runs `python -m csvstats` with `sys.executable` to prove the `__main__` wiring and the real exit code.

**Blocked by:** 01 (Summarize a CSV file's numeric columns)

**Status:** done

- [x] `-` reads stdin and prints the same summary as the equivalent file
- [x] A missing file prints `csvstats: error: <file>: <reason>` to stderr, prints nothing to stdout, and returns 2
- [x] A directory passed as the file returns 2 with the same error format
- [x] Invalid UTF-8 input and a `csv.Error` during parsing return 2 with the same error format, and nothing goes to stdout
- [x] No argument and two arguments raise `SystemExit` with code 2 and a usage message on stderr (tests capture this with `redirect_stderr`)
- [x] `--help` raises `SystemExit` with code 0 and describes the `file` argument and `-`
- [x] One subprocess smoke test checks real stdout and exit code through `python -m csvstats`
- [x] Each case has a test through `main` (or the smoke test), with no tests on internals
