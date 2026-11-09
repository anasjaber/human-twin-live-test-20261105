---
title: csvstats command-line tool
slug: csvstats-cli
labels: [ready-for-agent]
---

# csvstats command-line tool

## Problem Statement

When I have a CSV file I want a quick numeric summary of it (how many values each column holds, the smallest, the largest and the average) without opening a spreadsheet, writing a one-off script or installing anything like pandas. Real-world CSVs are messy: some cells are blank, some columns are text, some numeric columns have stray `n/a` values. I want one command that copes with all of that. I also want it in shell pipelines (`... | csvstats -`), and I want it to fail clearly when I mistype a file name.

## Solution

A small command-line tool, `csvstats`, written in Python 3.10+ using only the standard library. It is run as `python -m csvstats FILE`, or `python -m csvstats -` to read from stdin. It reads a CSV whose first row is a header and prints one line for each column that has at least one numeric value, in file order:

```
<column> <count> <min> <max> <mean>
```

`count` is the number of numeric cells in the column. `mean` is always printed with exactly two decimals. Blank and non-numeric cells are skipped. A column with no numeric cells is left out of the output. If the file does not exist, the tool prints an error to stderr and exits with code 2. The README gets a short usage section.

Example input:

```
name,age,score,city
alice,30,88.5,Paris
bob,,92,Berlin
carol,25,n/a,Rome
```

Example output:

```
age 2 25 30 27.50
score 2 88.5 92 90.25
```

## User Stories

1. As a data analyst, I want to run `csvstats` on a CSV file, so that I get a numeric summary of every column without writing code.
2. As a data analyst, I want one output line per numeric column, so that I can scan the summary quickly.
3. As a data analyst, I want each line to show the column name, count, min, max and mean in that order, so that the output is predictable.
4. As a data analyst, I want the columns listed in the same order as the file's header, so that I can match the output to the file.
5. As a data analyst, I want the mean always shown with exactly two decimals, so that the values line up and are easy to compare.
6. As a data analyst, I want blank cells skipped, so that missing data does not break the stats or count as zero.
7. As a data analyst, I want non-numeric cells (such as `n/a` or `-`) in an otherwise numeric column skipped, so that a few dirty values do not hide the whole column.
8. As a data analyst, I want text-only columns (names, cities) left out of the output, so that I only see meaningful numeric summaries.
9. As a data analyst, I want a column that is entirely blank left out, so that empty columns do not add noise.
10. As a data analyst, I want `count` to be the number of numeric values actually used, so that I know how much data each statistic is based on.
11. As a data analyst, I want integers and decimals in the same column treated alike, so that a column like `1, 2.5, 3` is summarized correctly.
12. As a data analyst, I want negative numbers and scientific notation (`-3`, `1e3`) recognized as numbers, so that scientific and financial data works.
13. As a data analyst, I want whole-number min and max shown without a trailing `.0`, so that integer columns read naturally.
14. As a data analyst, I want spaces around a number (`" 42 "`) tolerated, so that slightly sloppy files still work.
15. As a data analyst, I want quoted fields with embedded commas or newlines handled correctly, so that standard CSV exports parse properly.
16. As a data analyst, I want a UTF-8 byte-order mark at the start of the file ignored, so that files exported from Excel do not get a garbled first column name.
17. As a data analyst, I want short rows (fewer cells than the header) treated as having blank cells, so that ragged files still produce a summary.
18. As a data analyst, I want extra cells beyond the header width ignored, so that ragged files do not crash the tool.
19. As a shell user, I want to pass `-` as the file argument to read stdin, so that I can pipe data into the tool.
20. As a shell user, I want the summary on stdout and errors on stderr, so that I can redirect them separately.
21. As a shell user, I want a clear error on stderr and exit code 2 when the file does not exist, so that scripts can detect the failure.
22. As a shell user, I want the same error-and-exit-2 behaviour when the input cannot be read (a directory, no permission, not valid UTF-8), so that every input problem is handled the same way.
23. As a shell user, I want exit code 0 on success, even when no column is numeric, so that "nothing to report" is not treated as an error.
24. As a shell user, I want a usage message and a non-zero exit when I give no file argument or too many, so that I know how to call the tool.
25. As a shell user, I want `--help` to explain the arguments, so that I don't need the README to use the tool.
26. As a shell user, I want an empty file or a header-only file to produce no output and exit 0, so that empty inputs are harmless in pipelines.
27. As a user on a locked-down machine, I want the tool to need nothing beyond the Python standard library, so that I can use it without network access or pip.
28. As a user with a large file, I want the tool to process rows as a stream, so that memory does not grow with the file size.
29. As a new user, I want a short usage section in the README, so that I can learn the command, its output format and its exit codes at a glance.
30. As a maintainer, I want tests that run with `python -m unittest` and no third-party packages, so that anyone can verify the tool offline.
31. As a maintainer, I want the tests to drive the tool through its command-line entry point, so that they check the behaviour users rely on rather than internal helpers.

## Implementation Decisions

- **Shape**: one small, self-contained Python package named `csvstats`, runnable with `python -m csvstats`. No third-party dependencies, no packaging metadata and no installed console script. Targets Python 3.10+, so it must not use 3.11+-only features.
- **Entry-point interface (the test seam)**: one function, `main(argv, stdin, stdout, stderr) -> int`.
  - `argv` is the argument list without the program name.
  - The three streams are text streams. They default to the `sys` streams when not passed.
  - It returns the process exit code instead of calling `sys.exit` itself. The `__main__` module just does `sys.exit(main(sys.argv[1:]))`.
  - The one exception is argparse's own usage errors and `--help`. These raise `SystemExit` (code 2 for usage errors, 0 for help) and write to the real `sys.stderr`/`sys.stdout`, which tests capture by redirection. Recommended: let argparse do this rather than override it.
- **Internal split** (deep module behind the entry point): a pure `summarize(rows) -> list[ColumnStats]` function takes parsed CSV rows (header first) and returns stats for the numeric columns in header order. `main` handles arguments, opening the input, CSV parsing, formatting and exit codes. `summarize` is an implementation detail and is not a separate test seam.
- **Arguments**: exactly one positional argument, `file`. The value `-` means read stdin. No options other than `--help`.
- **Reading input**:
  - Files are opened in text mode with `utf-8-sig` encoding (which strips a BOM) and `newline=""`, as the `csv` module requires. Stdin is read from the given text stream as-is.
  - Parsing uses `csv.reader` with the default (comma, `"` quoting) dialect.
  - Rows are processed as a stream. Only a running count, min, max and a bounded list of non-overlapping sum partials are kept per column; numeric cells and rows are not retained.
- **Numeric cell rule**: strip surrounding whitespace. If the result is empty, skip the cell. Otherwise try `float()`. If that fails, skip the cell. Also skip non-finite results (`nan`, `inf`, `-inf`) so one stray `NaN` does not poison the min, max and mean. So any string Python's `float()` accepts as a finite number counts as numeric, including `1e3`, `+5` and `1_000`.
- **Columns**:
  - Identified by position, not name. Duplicate header names each get their own output line.
  - Rows shorter than the header have their missing cells treated as blank. Cells beyond the header width are ignored.
  - A column with zero numeric cells is omitted.
- **Output format**: one line per numeric column, with single spaces between fields: `name count min max mean`.
  - `name` is the header cell exactly as parsed. It is not quoted or escaped, so a name containing spaces makes that line ambiguous to split. This is accepted.
  - `count` is a plain integer.
  - `min` and `max` are printed as an integer when the value is whole (`30`, not `30.0`), otherwise in Python's shortest `repr` form (`88.5`).
  - `mean` is `sum / count` formatted with exactly two decimals (`27.50`), so it uses Python's float rounding. Sums are computed with `math.fsum` over the streaming partials for accuracy. If a running sum overflows, its mean remains `inf` or `-inf` with the overflow sign, even if later cells would cancel it; count and bounds continue updating, other columns still print, and exit code remains 0. These overflow markers are exceptions to the two-decimal format.
- **Exit codes and errors**:
  - `0` on success, including when nothing is printed: empty input, header only, or no numeric columns.
  - `2` when the input cannot be opened or read. This covers a missing file, a directory, permission denied and invalid UTF-8. It also covers a `csv.Error` raised during parsing.
  - The error message goes to stderr in the form `csvstats: error: <file>: <reason>`. Nothing is written to stdout in that case.
  - `2` for argparse usage errors, which is argparse's own behaviour.
- **README**: add a short "Usage" section. It shows the invocation (file and `-`), the output line format with a small example, the skipping and omission rules, and the exit codes. It also says how to run the tests.

## Testing Decisions

- **What makes a good test here**: tests check only externally visible behaviour, meaning the text on stdout, the text on stderr and the exit code for given arguments and input. They do not call `summarize` or other internals and do not assert on internal data structures. That way the internals can be refactored freely.
- **The single seam**: `main(argv, stdin, stdout, stderr)`, called in-process with `io.StringIO` streams.
  - Input files are written to a `tempfile.TemporaryDirectory`. Stdin cases pass a `StringIO`.
  - Argparse usage and `--help` cases assert on `SystemExit.code` and capture output with `contextlib.redirect_stderr`/`redirect_stdout`.
  - This is the highest seam short of spawning a process, and it exercises the full CLI contract quickly.
- **Optional smoke test**: one test runs `python -m csvstats` through `subprocess` with `sys.executable`, to prove the `__main__` wiring and the real exit code. It goes through the same public contract and does not add a new seam.
- **Framework**: standard-library `unittest` only. Tests live in a top-level `tests` package (with an `__init__.py`) so that `python -m unittest` discovers them from the repo root with no arguments.
- **Cases to cover**:
  - the example from this spec
  - column order
  - mean formatting, including rounding and a whole-number mean (`.00`)
  - integer versus decimal min/max formatting
  - blank and non-numeric cells skipped and counted correctly
  - all-text and all-blank columns omitted
  - negative numbers and scientific notation
  - whitespace-padded numbers
  - `nan`/`inf` skipped
  - quoted fields with commas and newlines
  - BOM stripped
  - short and long rows
  - duplicate header names
  - stdin via `-`
  - empty input and header-only input (no output, exit 0)
  - missing file (stderr message, empty stdout, exit 2)
  - a directory passed as the file (exit 2)
  - no argument and two arguments (exit 2)
- **Prior art**: none. The repo has no code or tests yet, so these tests set the convention.

## Out of Scope

- Delimiters other than comma, dialect sniffing, and options for quoting or encoding.
- Files without a header row.
- Statistics beyond count, min, max and mean (median, stddev, sum and so on).
- Output formats other than the space-separated line (JSON, CSV, aligned tables, a header line).
- Choosing columns or filtering rows.
- Locale-aware number parsing (`1,5`, `1.000,00`), currency symbols, percentages and thousands separators other than Python's `_`.
- Packaging, a `pyproject.toml`, a console-script entry point, or publishing to PyPI.
- Reading several files in one call.

## Further Notes

- The repo currently contains only a README, and there is no GLOSSARY.md or docs/adr/, so there was no existing vocabulary or ADR to follow. Terms used here: **numeric cell** (a cell that passes the numeric cell rule), **numeric column** (a column with at least one numeric cell).
- "Rounded to 2 decimals" is read as "formatted with exactly two decimals" (`27.50`, not `27.5`), which keeps the output aligned.
- Because the output is space-separated, header names that contain spaces make lines ambiguous to parse by machine. Fixing this (quoting, or a tab separator) would break the requested format, so it is left as-is.

## Open questions

Nobody was available to answer during this step, so each question below has the recommended answer, chosen by the spec author.

1. **Do these test seams match expectations?** (asked by the skill) — Yes. There is one seam: the in-process `main(argv, stdin, stdout, stderr) -> int` entry point, driven with `StringIO` streams and temp files, plus at most one subprocess smoke test through the same public contract. Internal helpers are not tested directly.
2. **How is the tool invoked without pip?** — As `python -m csvstats`, from a `csvstats` package. No console script.
3. **What counts as numeric?** — Anything Python's `float()` accepts after whitespace is stripped, excluding `nan` and `±inf`.
4. **How are min/max formatted?** — As an integer when the value is whole, otherwise the shortest float `repr`. The mean always has exactly two decimals.
5. **Is the mean "rounded" or "formatted" to 2 decimals?** — Formatted with exactly two decimals (`f"{x:.2f}"`).
6. **Which other input failures besides a missing file exit with 2?** — All input open and read failures: a directory, permission denied, invalid UTF-8 and `csv.Error`. They use the same `csvstats: error: <file>: <reason>` message.
7. **What about empty input, header-only input, or no numeric columns?** — No output, exit 0.
8. **What about ragged rows?** — Missing cells count as blank and extra cells are ignored.
9. **What about duplicate header names?** — Columns are identified by position, and each one gets its own line.
10. **Encoding and BOM?** — Files are read as UTF-8 with the BOM stripped (`utf-8-sig`). Stdin uses the stream as given.
11. **Exit code for a wrong number of arguments?** — 2, argparse's default, with its usage message on stderr.
12. **Where do the tests live and how are they discovered?** — In a top-level `tests` package, found by plain `python -m unittest` run from the repo root.
13. **Which triage label?** — `ready-for-agent`, recorded in the spec's front matter, because the tracker is local markdown.
