# 04: README usage section

**What to build:** A new user can learn the tool from the README alone. Add a short "Usage" section covering:

- the invocation, with a file and with `-` for stdin
- the output line format, `<column> <count> <min> <max> <mean>`, with a small example
- the skipping and omission rules (blank and non-numeric cells skipped, columns with no numeric cells left out, mean shown with two decimals)
- the exit codes: 0 for success (even with no output), 2 for input errors and usage errors
- how to run the tests: `python -m unittest`

**Blocked by:** 02 (Handle messy real-world CSV shapes), 03 (Shell contract: stdin, input errors and exit codes)

**Status:** done

- [x] README has a "Usage" section showing both `python -m csvstats FILE` and `python -m csvstats -`
- [x] It shows the output format with an example that matches what the tool actually prints
- [x] It states the skipping and omission rules and the mean formatting
- [x] It lists exit codes 0 and 2 and when each happens
- [x] It says how to run the tests
