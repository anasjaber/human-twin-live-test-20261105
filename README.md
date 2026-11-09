# human-twin-live-test-20261105
Throwaway repo for a Human Twin live test (2026-11-05). Safe to delete.

## Usage

Requires Python 3.10+ and only the standard library. Run from the repository root:

```sh
python -m csvstats FILE
python -m csvstats - < data.csv
```

Use `-` to read CSV from stdin. Use `--help` for argument help. The first CSV
row is the header. Each numeric column produces a line, in header order:

```text
<column> <count> <min> <max> <mean>
```

For example, given `data.csv`:

```csv
name,age,score
alice,30,88.5
bob,,92
carol,25,n/a
```

`python -m csvstats data.csv` prints:

```text
age 2 25 30 27.50
score 2 88.5 92 90.25
```

Blank, non-numeric and non-finite (`nan`, `inf`, `-inf`) cells are skipped.
Columns without numeric cells are omitted. Count includes only numeric cells;
whole-number min/max have no trailing `.0`, and the mean always has two decimals.
If a running sum overflows, its mean stays `inf` or `-inf` with that sign,
even after later cancellation; counts, bounds and other columns still work.
Rows are processed as a stream, including quoted CSV fields and ragged rows.

Exit code **0** means success, including empty inputs or no numeric columns.
Exit code **2** means an input or usage error. Summaries go to stdout; errors go
to stderr.

Run the tests from the repository root:

```sh
python -m unittest
```

If your system names Python 3 `python3`, use that in place of `python` above.
