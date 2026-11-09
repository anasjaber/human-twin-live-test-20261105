# Code review: csvstats-cli

Fixed point: `36fecb44ae49e63615decb84525df958ca02cbc2`. Diff reviewed: `git add -A && git diff --cached 36fecb4` (13 files, +562 lines).
Spec: `.scratch/csvstats-cli/spec.md` and tickets `issues/01`–`04`.
Standards sources: the repo has no CODING_STANDARDS.md, CONTRIBUTING.md, AGENTS.md, GLOSSARY.md or docs/adr/. The spec's implementation and testing decisions and the README were used as the documented standards, together with the Fowler smell baseline.

## Standards

The code follows most of the documented conventions:
- It uses only the standard library and runs on Python 3.10.
- There is a single `main(argv, stdin, stdout, stderr) -> int`, and `__main__` only calls `sys.exit(main(sys.argv[1:]))`.
- Errors use the format `csvstats: error: <file>: <reason>`.
- Files are opened with `utf-8-sig` and `newline=""`.
- Tests use only `unittest`, and none of them call `summarize`.

### Documented-standard breaches

1. **`csvstats/__init__.py`, `ColumnStats` / `add` (hard, small).** The spec says "Only a running count, min, max and **sum** are kept per column" and "Sums are computed with `math.fsum`". The code instead keeps a `partials: list[float]` per column, updates it with a copy of fsum's partial-sums loop, and calls `math.fsum(partials)` at the end. The two spec lines can't both hold, because `fsum` can't run incrementally. Recommended fix: reword the spec to match the code.

### Baseline smells (judgement calls)

- **Duplicated Code: `ColumnStats.add`.** It contains a hand-written copy of `math.fsum`'s algorithm (`high = value + partial; low = partial - (high - value)`), and the result is then passed to the real `math.fsum`. Add a comment explaining why, or move the logic into a small accumulator type.
- **Feature Envy: `main`.** `mean = math.fsum(column.partials) / column.count` reaches into the internals of `ColumnStats`. A `ColumnStats.mean` property would keep that inside the class.
- **Duplicated Code: `tests/test_shell.py`.** `test_missing_file_reports_error`, `test_directory_reports_error` and `test_invalid_utf8_produces_no_partial_output` repeat the body of `assert_error` inline. `test_stdin_read_failure_reports_error` repeats the stream capture from `invoke`. `ShellTests.invoke` and `FileCase.run_csv` both wrap the same `StringIO` capture.
- **Test helper placement / Mysterious Name: `tests/test_shapes.py`.** It imports `from tests.test_stats import FileCase`, so one test module depends on another. The shared helper would be better in its own module, such as `tests/support.py`. `CsvFileCase` would also be a clearer name.
- **Minor inconsistency: `main`.** `stdout` and `stderr` fall back to the `sys` streams at the top of the function, but `stdin` falls back inline inside the `try`.
- **Mysterious Name (minor): `partials`.** The name only makes sense if you already know the fsum algorithm. `sum_partials` would be clearer.

## Spec

All 21 tests pass under `python3 -m unittest`, and every acceptance box in tickets 01–04 holds.

### (a) Missing or partial

None. Checked by hand:
- the spec example and header order
- blank and `n/a` cells skipped; `1_000` and `+5` counted
- duplicate headers kept separate; short and long rows
- empty input: no output, exit 0
- missing file and directory: exit 2, empty stdout, error on stderr

### (b) Scope creep

There is no feature creep. The README adds a `python3` hint and a note that rows are streamed. The tests add permission-denied and stdin-read-failure cases, which the spec allows.

### (c) Implemented but looks wrong

1. **Overflowing sums crash with a traceback (confirmed).**
   - Spec: "`0` on success … `2` when the input cannot be opened or read".
   - Repro: `printf 'a,b\n1e308,1\n1e308,2\n' | python3 -m csvstats -` fails with `ValueError: -inf + inf in fsum` at `csvstats/__init__.py:76`, prints nothing on stdout (not even column `b`), and exits 1.
   - Cause: every cell is a valid numeric cell, but the partials loop overflows to ±inf.
   - The spec doesn't cover overflow; a plain `math.fsum` would raise `OverflowError` too.
   - Recommended fix: catch the error and print `inf`/`-inf` (or `nan`) for that column's sum/mean, so the other columns still print and the exit code stays 0. Add a test for it.
2. **The running state per column is a list, not a single sum.** This is the same point as Standards item 1.
   - Spec: "Only a running count, min, max and sum are kept per column."
   - The list stays small in practice, so memory use doesn't grow with the input. Still, the spec and the code should say the same thing.
3. **Minor: the error reason repeats the path.**
   - Example: `csvstats: error: /tmp: [Errno 21] Is a directory: '/tmp'`.
   - The format still matches `<file>: <reason>`, but using `error.strerror` would read more cleanly.

Checked and not a defect:
- A BOM on stdin is kept, which matches "Stdin is read … as-is".
- An unclosed quote at EOF gives empty output and exit 0, which is how the default `csv` dialect behaves.

---

**Summary:** Standards: 1 documented breach + 6 smells. The worst is the per-column `partials` list, which goes against "running … sum". Spec: 3 findings, 0 missing requirements. The worst is the uncaught `ValueError` when sums overflow (exit 1 with a traceback, outside the exit-code contract).


## Resolution

- Standards 1 (hard): Fixed the spec and ticket 01 to describe bounded streaming sum partials finalized with `math.fsum`, as recommended.
- Duplicated Code / ColumnStats.add: Added an explanation of why error-free addition partials are needed for streaming accuracy without retaining cells.
- Feature Envy / main: Moved mean calculation behind `ColumnStats.mean`.
- Duplicated Code / tests: Centralized stream capture and error assertions in `tests/support.py`; reused them for file and stdin failures.
- Test helper placement / name: Moved the shared file helper to `tests/support.py` and renamed it `CsvFileCase`.
- Stream defaults: Resolved stdin alongside stdout and stderr at the start of `main`.
- Mysterious Name / partials: Renamed to `sum_partials`.
- Spec (c) 1 / overflow: Fixed with signed infinity on running-sum overflow; other columns and exit 0 are preserved. Positive and negative regression cases failed first, then passed. Documented sticky overflow and the formatting exception.
- Spec (c) 2 / running state: Fixed by the same spec and ticket clarification as Standards 1.
- Spec (c) 3 / repeated path: Use `OSError.strerror` when available, with a fallback for other errors; regression failed first, then passed.

Selected the recommended existing public `main` test seam without questions, as required for this run. No missing requirements or scope-creep findings required changes.
