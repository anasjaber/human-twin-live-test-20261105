# Code review: wordfreq-cli

- Fixed point: `4ff30aaebe56b324272356ac53aea5718437a1d3` (Baseline). Reviewed with `git diff --cached` after `git add -A`.
- Spec: `.scratch/wordfreq-cli/spec.md` and tickets 01–03 in `.scratch/wordfreq-cli/issues/`.
- Standards sources: the repo has no CODING_STANDARDS.md, CONTRIBUTING.md, AGENTS.md, CLAUDE.md, GLOSSARY.md or docs/adr/. The Standards axis therefore uses the Fowler smell baseline, PEP 8 conventions, and README.md as the stated usage contract.

## Standards

There are no hard violations. The repo documents no coding standard, and the code doesn't contradict anything README.md claims: Python 3.10+, stdlib only, exit 0 on success, exit 2 for errors, `--top` must be positive, invalid UTF-8 is replaced, and help output is right. Everything below is a judgement call, mostly minor and mostly in the tests.

**`wordfreq/__init__.py`**
- **Possible Divergent Change (long `main`).** `main` parses arguments, picks and decodes the input, handles file errors and formats the output. Pulling out something like `_read_text(path, stdin) -> str` would separate input handling from the rest.
- **Possible Mysterious Name (unnamed literal).** `re.findall(r"[^\W_]+(?:'[^\W_]+)*", text.lower().replace("’", "'"))` puts the tokenisation rule inline. A named constant such as `WORD_PATTERN`, plus a name for the curly-apostrophe step, would state the rule.
- **Small repetition.** The `X if X is not None else sys.X` pattern appears three times (`output`, `error_output`, `source_input`). It's minor, so leaving it is fine.

**`tests/test_wordfreq.py`**
- **Possible Speculative Generality (dead code in `assert_usage_error`).** `main` already catches `SystemExit` and returns the code, so the `except SystemExit` branch, the `redirect_stderr(terminal)` wrapper and the `terminal` buffer never run. The helper can shrink to its last two assertions.
- **Possible Duplicated Code.**
  - `test_module_runs_as_a_process`, `test_missing_file_process_exit_code` and `test_process_stdin_replaces_invalid_utf8` repeat the same `subprocess.run([sys.executable, "-m", "wordfreq", ...], capture_output=True, ...)` shape. A `run_process(*args, input=None)` helper would cover all three.
  - The `startswith(f"wordfreq: error: {path}: ")` assertion is duplicated between `test_unreadable_paths` and `test_missing_file_process_exit_code`.
- **Possible Repeated Switches (`test_permission_and_read_errors`).** `if isinstance(error, PermissionError): ... else: ...` inside the subtest loop means each case has its own setup. Two separate tests would read more clearly than a loop that branches on type.
- **Possible Mysterious Name (minor).** `boundary`, `opened` and `terminal` don't say what they hold. For example, `boundary` could be `open_patch`.
- **PEP 8 (imports at top of module).** `from contextlib import redirect_stderr` and `from unittest.mock import mock_open, patch` are imported inside methods. They should be module-level imports.

**`wordfreq/__main__.py`, `.gitignore`, `README.md`:** clean. Import order and line length are left to tooling.

## Spec

The change conforms to the spec and all three tickets, with no blocking findings. All 15 tests pass under `python3 -m unittest`.

**Edge cases checked and conforming:**
- **Tokenisation:** contractions stay whole (`don't`, `o'clock`, `rock'n'roll`), and the curly `don’t` merges into `don't`. Quoted `'x'` and `'tis` lose their outer apostrophes. `a''b` gives `a` and `b`. `foo_bar`, `well-known`, `x—y` and `z–w` all split. `2024` and `mp3` are counted as words. `café`, `CAFÉ` and `naïve` are counted intact.
- **Ranking:** ties sort in plain string order (`1, 10, 11, … 2`). The default is 10 lines.
- **Empty or punctuation-only input:** no output, exit 0.
- **`--top`:** `0`, `-3`, `abc` and `2.5` each give a usage message on stderr, empty stdout and exit 2.
- **Errors:** a missing file, a directory, or no file argument each give a `wordfreq: error: ...` message on stderr and exit 2.
- **Invalid UTF-8:** bytes on real stdin are replaced and the run exits 0.
- **`--help`:** documents `-` for stdin and the default of 10.

The permission-denied case was not run by hand. It takes the same `OSError` path as the missing-file case and is covered by `test_permission_and_read_errors`, which passes.

**(a) Missing or partial:** none found.

**(b) Scope creep (minor):**
- **Extra subprocess test.** The spec says "**One end-to-end smoke test** runs `python -m wordfreq` via `subprocess`". Ticket 03 allows "(or a second subprocess test)". There are three; the extra one is `test_process_stdin_replaces_invalid_utf8`. It goes beyond what was asked, but it is the only check on the real-stdin decoding path.
- **`.gitignore`.** No spec line asks for it. It's harmless.

**(c) Implemented but questionable (low severity, edge cases only):**
- **Characters that aren't letters or digits count as word characters.** The spec says "A word is a maximal run of Unicode letters and digits". `[^\W_]` matches what `str.isalnum()` accepts, which includes other numeric characters: `x²` is one word, and `½` and `Ⅳ` are counted as words.
- **Decomposed accents split words.** For "non-ASCII letters (e.g. "café", "naïve") treated as word characters", a `café` written with a separate combining accent (`cafe` + U+0301) is counted as `cafe`. It does not merge with the precomposed `café`. A combining accent isn't strictly a letter, so this arguably conforms, but Unicode normalisation is an open decision.

---

**Summary:** Standards has 0 hard violations and 9 judgement calls; the most significant is the dead `SystemExit` branch in the `assert_usage_error` test helper. Spec has 0 missing, 2 minor scope-creep and 2 low-severity questionable findings; the most significant is that the word regex accepts characters like `²`, `½` and `Ⅳ` beyond what "letters and digits" says.

## Resolution

- Long `main`: fixed by extracting `_read_text(path, stdin)`; existing CLI tests cover file and stdin reading.
- Inline tokenisation rule: fixed with `WORD_PATTERN` and `_normalise_word_characters`, naming apostrophe normalization and character filtering.
- Repeated stream defaults: retained; explicit defaults are clearer than a helper for three small expressions.
- Dead usage-error handling: fixed by removing the unreachable `SystemExit` fallback, terminal buffer and redirect wrapper.
- Repeated subprocess setup: fixed with `run_process`, preserving all three real CLI checks.
- Repeated path-error assertion: fixed with `assert_path_error`, shared by in-process and subprocess checks.
- Branching permission/read-error test: fixed by splitting into separate permission-error and read-error tests.
- Mysterious test names: fixed by removing `boundary` and `terminal` and naming the mocked file `input_file`.
- Method-local imports: fixed; mock imports are module-level and the unused redirect import is removed.
- Missing or partial spec implementation: none identified; no additional feature work needed.
- Extra subprocess test: retained because only this check exercises malformed UTF-8 through the real stdin buffer; removing it would lose useful behavioral coverage.
- Unrequested `.gitignore`: retained because it excludes generated Python caches without affecting CLI behavior.
- Non-letter/non-digit numbers accepted as words: fixed test-first through `main`; Unicode letter categories and decimal digits are accepted, while `²`, `½` and `Ⅳ` separate words. README documents this interpretation of digits.
- Decomposed accents: unchanged because combining marks are separators under the explicit word rule; normalization would change that rule. README makes this limitation explicit.
- Test-seam confirmation: selected the recommended existing `main` seam and retained subprocess checks of the same interface, per the run's instruction to choose without asking questions.
- Validation: baseline 15 tests passed; the new numeric-character regression failed before the fix and passed afterward; full `python3 -m unittest` suite passes all 17 tests.
