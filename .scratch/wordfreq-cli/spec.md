---
title: wordfreq command-line tool
slug: wordfreq-cli
labels: [ready-for-agent]
status: open
---

# wordfreq command-line tool

## Problem Statement

I have plain text files (or text coming out of another command) and want to know which words occur most often. Today the repository has no tool for this, and doing it by hand with shell pipelines (`tr | sort | uniq -c | sort -rn`) is fiddly: case and punctuation get in the way, ties come out in an unpredictable order, and the result is hard to reuse in scripts. I want one small, dependency-free command that gives a clean, deterministic "top N words" list.

## Solution

A `wordfreq` command-line tool written in Python 3.10+ using only the standard library. Given a text file path (or `-` for standard input), it counts words case-insensitively, ignoring punctuation, and prints the N most frequent words, one per line, as `word count`. The most frequent words come first; words with the same count are listed alphabetically. `--top N` controls how many lines are printed (default 10). If the file doesn't exist, it prints an error to standard error and exits with code 2. The README gets a short usage section, and the behaviour is covered by `unittest` tests that run with `python -m unittest`.

## User Stories

1. As a command-line user, I want to run `wordfreq <file>`, so that I can see the most frequent words in a text file.
2. As a command-line user, I want the output to default to the top 10 words, so that I get a useful summary without passing options.
3. As a command-line user, I want to pass `--top N`, so that I can choose how many words are shown.
4. As a command-line user, I want each output line to be `word count` with a single space between them, so that the output is easy to read and to parse.
5. As a command-line user, I want the most frequent word printed first, so that the ranking is obvious.
6. As a command-line user, I want words with equal counts ordered alphabetically, so that the output is deterministic and repeatable between runs.
7. As a command-line user, I want "The", "the" and "THE" counted as the same word, so that capitalisation at the start of sentences doesn't split counts.
8. As a command-line user, I want words printed in lowercase, so that the displayed form is consistent with case-insensitive counting.
9. As a command-line user, I want punctuation such as commas, full stops, quotes, brackets and dashes ignored, so that "word," and "word" count as the same word.
10. As a command-line user, I want contractions such as "don't" kept as a single word, so that they aren't split into meaningless fragments like "don" and "t".
11. As a command-line user, I want leading and trailing apostrophes (e.g. quoted 'word') to be dropped, so that quoting doesn't create distinct words.
12. As a command-line user, I want hyphenated or dash-joined text like "well-known" split into separate words, so that punctuation never becomes part of a word.
13. As a command-line user, I want digits to count as word characters, so that tokens such as "2024" or "mp3" are counted rather than silently dropped.
14. As a command-line user, I want non-ASCII letters (e.g. "café", "naïve") treated as word characters, so that text in other languages is counted correctly.
15. As a shell scripter, I want to pass `-` as the file argument, so that I can pipe text from another command into wordfreq.
16. As a shell scripter, I want stdin reading combined with `--top N`, so that I can limit piped results too.
17. As a command-line user, I want fewer than N lines printed when the input has fewer than N distinct words, so that the tool never pads or errors on small inputs.
18. As a command-line user, I want empty input (or input with only punctuation/whitespace) to produce no output and exit 0, so that empty files are not treated as errors.
19. As a command-line user, I want a missing file to print a clear error message on standard error, so that I know what went wrong.
20. As a shell scripter, I want a missing file to exit with code 2, so that my scripts can detect the failure.
21. As a shell scripter, I want error messages to go only to standard error and nothing to standard output on failure, so that pipelines aren't polluted with partial output.
22. As a command-line user, I want other unreadable paths (a directory, a permission-denied file) to be reported the same way as a missing file (stderr message, exit 2), so that all input problems behave consistently.
23. As a command-line user, I want `--top` with a non-integer, zero or negative value rejected with a usage error (exit 2), so that I don't get confusing empty or nonsensical output.
24. As a command-line user, I want `--help` to describe the file argument and `--top`, so that I can learn usage without reading the source.
25. As a command-line user, I want a usage error when no file argument is given, so that the tool doesn't silently hang waiting on stdin.
26. As a shell scripter, I want successful runs to exit 0, so that I can chain wordfreq with `&&`.
27. As a command-line user, I want the input decoded as UTF-8 with undecodable bytes replaced rather than crashing, so that slightly malformed files still produce results.
28. As a command-line user, I want words separated by any whitespace, including newlines and tabs, so that multi-line files are counted correctly.
29. As a user on a machine without network access, I want the tool to need only the Python standard library, so that I can run it without installing anything.
30. As a user, I want to run the tool with `python -m wordfreq`, so that it works straight from a checkout without installation.
31. As a new user reading the README, I want a short usage section with examples, so that I can start using the tool immediately.
32. As a contributor, I want the tests to run with `python -m unittest` from the repository root, so that I can verify changes with no extra tooling.
33. As a contributor, I want the tests to exercise the tool's external behaviour (arguments in, output/exit code out), so that I can refactor internals without rewriting tests.

## Implementation Decisions

- **Module layout**: a single small Python package named `wordfreq`, runnable as `python -m wordfreq`. It contains two small pieces:
  - a pure counting function that takes text and returns the full ranked list of `(word, count)` pairs, already sorted, and
  - a CLI entry point `main(argv=None, stdin=None, stdout=None, stderr=None) -> int` that parses arguments, reads input, calls the counting function, writes output and returns the exit code. The streams default to `sys.stdin`/`sys.stdout`/`sys.stderr` when not supplied. The package's `__main__` calls `sys.exit(main())`.
- **Argument parsing**: `argparse`. One required positional argument `file` (a path, or `-` for stdin). One option `--top N` (integer, default 10). `--top` must be a positive integer (≥ 1). argparse rejects values that are not integers, zero or negative as usage errors: exit code 2, usage message on stderr.
- **Tokenisation rule** (the definition of a "word"):
  - Lowercase the text (`str.lower()`).
  - A word is a maximal run of Unicode letters and digits, optionally containing single internal apostrophes between word characters (e.g. `don't`, `o'clock`). Underscore is not a word character.
  - Every other character (whitespace, punctuation, symbols, dashes, leading/trailing apostrophes) is a separator.
  - Both the straight apostrophe `'` and the typographic right single quote `’` count as apostrophes. Output always uses the straight apostrophe `'`.
- **Ranking**: sort by count descending, then word ascending (plain Python string ordering of the lowercased word). Output the first N entries.
- **Output format**: one line per word, `word count` separated by a single space, newline-terminated, nothing else (no header, no trailing summary).
- **Input reading**: files are opened as text in UTF-8 with `errors="replace"`. For `-`, read all of stdin as text. Reading the whole input at once is fine; streaming is not required.
- **Error handling**: any `OSError` while opening or reading the named file (missing file, directory, permission denied) prints a single line `wordfreq: error: <path>: <reason>` to stderr, writes nothing to stdout, and returns 2. The missing-file case is the one the feature request requires; the other cases follow the same code path.
- **Exit codes**: 0 on success (including empty input), 2 on input errors and usage errors.
- **Dependencies**: Python 3.10+ standard library only. No packaging metadata (pyproject/setup) is required. The supported way to run the tool is from a checkout.
- **README**: add a "Usage" section showing `python -m wordfreq FILE`, `--top N`, stdin via `-`, the output format, the exit code 2 on missing files, and how to run the tests.

## Testing Decisions

- **What makes a good test here**: tests assert only external behaviour: given arguments and input text, what is printed to stdout/stderr and what exit code is returned. They don't reach into tokeniser internals, regexes or private helpers, so the implementation can change freely.
- **Test seam (one seam)**: the CLI entry point `main(argv, stdin, stdout, stderr) -> int`. Tests pass `argv` lists, `io.StringIO` objects for the streams, and temporary files (via `tempfile`) for file inputs. This is the highest seam that still runs fast and in-process. It covers parsing, reading, counting, ranking, formatting and error handling in one place.
  - argparse usage errors raise `SystemExit(2)`. `main` may let that propagate or catch it and return the code; either is fine as long as the observable exit code is 2 and the message goes to stderr. Tests should keep argparse's message off the real terminal, either by redirecting `sys.stderr` (`contextlib.redirect_stderr`) or by having `main` route parser output to the injected stderr.
- **One end-to-end smoke test** runs `python -m wordfreq` via `subprocess` with `sys.executable`, to prove the `__main__` wiring and the real process exit code. It tests the same interface from outside the process rather than adding a new seam.
- **Behaviours to cover**: default top 10; `--top N`; fewer distinct words than N; tie-break alphabetical; case-insensitivity; punctuation ignored; contractions kept; hyphen splits; digits and non-ASCII letters; stdin via `-`; empty input → no output, exit 0; missing file → stderr message, empty stdout, exit 2; invalid `--top` (0, negative, non-integer) → exit 2.
- **Framework**: standard-library `unittest` only, discoverable by `python -m unittest` from the repository root. Test modules are named `test_*.py` and live where default discovery finds them, e.g. a `tests` package with an `__init__.py`.
- **Prior art**: none. The repository currently contains only a README, so these will be the first tests.

## Out of Scope

- Stop-word filtering, stemming or lemmatisation.
- Multiple input files in one invocation.
- Output formats other than `word count` lines (JSON, CSV, aligned columns).
- Options for case-sensitive counting, custom tokenisation or custom sort order.
- Streaming very large inputs with bounded memory.
- Packaging/installing a console script, publishing to PyPI, or CI configuration.
- Encodings other than UTF-8 (no `--encoding` option).

## Further Notes

- The repository has no GLOSSARY.md or docs/adr/, so no existing vocabulary or ADRs constrain this design. Terms used here: **word** (per the tokenisation rule above), **count** (number of occurrences of a word), **top N** (the first N entries of the ranking).
- The environment has no network access, so nothing may require `pip install`.

## Open questions

Nobody was available to answer these, so I picked the recommended answer for each.

1. **Test seams: do these match expectations?** *Answer:* Yes. Use one seam: the in-process CLI entry point `main(argv, stdin, stdout, stderr) -> int`, plus one `subprocess` smoke test of `python -m wordfreq` that tests the same interface from outside the process. No separate unit tests of the tokeniser.
2. **What exactly is a "word", and how is punctuation "ignored"?** *Answer:* Maximal runs of Unicode letters and digits, with single internal apostrophes allowed (`don't` stays one word). All other characters separate words, so `well-known` → `well`, `known`. Underscore is not a word character.
3. **Are digits words?** *Answer:* Yes, digits count as word characters.
4. **How is output displayed for mixed-case words?** *Answer:* Lowercase.
5. **What does `--top` accept?** *Answer:* Positive integers only. 0, negative or non-integer values are usage errors with exit code 2.
6. **What if there are fewer than N distinct words, or the input is empty?** *Answer:* Print whatever there is (possibly nothing) and exit 0.
7. **How are other unreadable paths (a directory, permission denied) handled?** *Answer:* The same way as a missing file: one-line message on stderr, nothing on stdout, exit 2.
8. **Which input encoding is used?** *Answer:* UTF-8 with `errors="replace"`, for both files and stdin.
9. **How is the tool invoked?** *Answer:* `python -m wordfreq`, with no packaging or console-script install.
10. **Is the file argument optional (default to stdin)?** *Answer:* No. It is required, and stdin is read only when it is `-`.
11. **Triage label?** *Answer:* `ready-for-agent`, recorded in the spec's front matter because the tracker is local markdown.
