# 02: Handle messy real-world CSV shapes

**What to build:** Real exports parse correctly and give sensible summaries:

- Quoted fields with embedded commas or newlines are parsed as single cells.
- A UTF-8 BOM at the start of a file does not get into the first column name.
- Short rows (fewer cells than the header) treat the missing cells as blank. Cells beyond the header width are ignored and don't crash the tool.
- Columns are identified by position, so duplicate header names each get their own output line.
- An empty file or a header-only file prints nothing and exits 0.

Much of this may already work after ticket 01. This ticket pins every case down with tests through `main` and fixes whatever doesn't hold.

**Blocked by:** 01 (Summarize a CSV file's numeric columns)

**Status:** done

- [x] Quoted fields containing commas and newlines are summarized correctly
- [x] A file starting with a UTF-8 BOM prints the first column name without the BOM
- [x] Short rows count missing cells as blank (not zero, not an error)
- [x] Extra cells beyond the header width are ignored
- [x] Duplicate header names produce one line per column, in position order
- [x] Empty input and header-only input print nothing and exit 0
- [x] Each case above has a test that calls only `main`
