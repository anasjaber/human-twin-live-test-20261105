# 01: Summarize a CSV file's numeric columns

**What to build:** The tracer bullet through the whole tool. A user runs `python -m csvstats FILE` on a CSV with a header row and gets one line per **numeric column** (a column with at least one **numeric cell**), in header order, as `<column> <count> <min> <max> <mean>`. Running it on the spec's example input prints exactly the spec's example output and exits 0.

This ticket sets up the package, the single test seam (`main(argv, stdin, stdout, stderr) -> int`, with `__main__` doing `sys.exit(main(sys.argv[1:]))`), the internal `summarize` split, and the top-level `tests` package that `python -m unittest` discovers from the repo root with no arguments. It also implements the full numeric cell rule and output formatting, since the spec example already depends on them:

- Numeric cell rule: strip whitespace; empty means skip; otherwise `float()`, skipping failures and non-finite values (`nan`, `inf`, `-inf`).
- Columns with zero numeric cells (all text or all blank) are left out.
- `count` is the number of numeric cells; `min`/`max` print as integers when whole, else shortest `repr`; `mean` is `math.fsum(values) / count` with exactly two decimals.
- Rows are streamed: only running count, min, max and bounded non-overlapping sum partials are kept per column.
- Files are opened with `utf-8-sig` and `newline=""` and parsed with the default `csv.reader` dialect. Argument handling uses argparse with exactly one positional `file`.

Standard library only, Python 3.10+ compatible. Tests drive only `main` with `io.StringIO` streams and temp files; they never call `summarize` directly.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] `python -m csvstats FILE` on the spec's example input prints `age 2 25 30 27.50` and `score 2 88.5 92 90.25` and exits 0
- [x] Output columns follow header order
- [x] Mean is always shown with two decimals, including rounding cases and a whole-number mean (`.00`)
- [x] Whole min/max print without `.0`; non-whole ones print in shortest `repr` (`88.5`)
- [x] Blank and non-numeric cells (`n/a`, `-`) are skipped and not counted
- [x] All-text and all-blank columns are left out
- [x] Negative numbers, scientific notation (`1e3`) and whitespace-padded numbers (`" 42 "`) are counted as numbers
- [x] `nan`, `inf` and `-inf` cells are skipped
- [x] A file with no numeric columns prints nothing and exits 0
- [x] Tests live in a top-level `tests` package, use only `unittest`, call only `main`, and pass with plain `python -m unittest` from the repo root
- [x] No third-party imports and no 3.11+-only features
