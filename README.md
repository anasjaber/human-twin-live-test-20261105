# human-twin-live-test-20261105
Throwaway repo for a Human Twin live test (2026-11-05). Safe to delete.

## Usage

Requires Python 3.10+ and only the standard library. Run from this checkout:

```sh
python -m wordfreq FILE
python -m wordfreq FILE --top 5
python -m unittest
```

Output is one `word count` pair per line, with the most frequent words first
and alphabetical ordering for ties. The default is the top 10 words.
Use `python3` if your system does not provide a `python` command.

Pipe UTF-8 text through standard input with `-`:

```sh
printf 'apple pear apple\n' | python -m wordfreq - --top 1
# apple 2
```

Words are lowercased Unicode letters and decimal digits, with internal apostrophes
retained. Other numeric characters (such as `²`, `½` and `Ⅳ`) separate words.
Combining marks are separators; decomposed accents are not normalized.
Punctuation separates words. Invalid UTF-8 bytes are replaced.
Successful runs (including empty input) exit 0. Missing or unreadable files
and usage errors exit 2, with errors on stderr and no output on stdout.
`--top` must be a positive integer. Run `python -m wordfreq --help` for help.
