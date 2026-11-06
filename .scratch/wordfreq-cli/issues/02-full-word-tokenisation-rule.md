# 02: Full word tokenisation rule (contractions, hyphens, digits, non-ASCII)

**What to build:** The counted **words** follow the spec's exact tokenisation rule, so real-world prose gives sensible counts. After lowercasing, a word is a maximal run of Unicode letters and digits, optionally with single internal apostrophes between word characters. Everything else separates words, including dashes, underscores and leading/trailing apostrophes. Both the straight apostrophe `'` and the typographic right single quote `’` count as apostrophes, and output always uses `'`.

Observable through the same `main` seam as ticket 01. Tests assert printed output only, not tokeniser internals.

**Blocked by:** 01 (Count and rank words in a file)

**Test location:** All tests live in `tests/test_wordfreq.py` (reviewer requirement).

**Status:** done

- [x] `don't` and `o'clock` are each counted as one word
- [x] `don’t` (typographic apostrophe) is counted together with `don't` and printed as `don't`
- [x] Quoted `'word'` counts as `word` (leading/trailing apostrophes dropped)
- [x] Consecutive apostrophes don't join words (e.g. `a''b` gives `a` and `b`)
- [x] `well-known` and dash-joined text (`word—word`, `word–word`) split into separate words
- [x] Underscore is a separator: `foo_bar` gives `foo` and `bar`
- [x] Digits are word characters: `2024` and `mp3` are counted as words
- [x] Non-ASCII letters are word characters: `café` and `naïve` are counted intact, and `Café`/`CAFÉ` merge into `café`
- [x] Tests cover contractions kept, hyphen splits, digits and non-ASCII letters through the CLI seam; `python -m unittest` passes
