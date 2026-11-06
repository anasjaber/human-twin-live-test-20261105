import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from wordfreq import main


class WordfreqTests(unittest.TestCase):
    def run_process(self, *args, input=None):
        return subprocess.run([sys.executable, "-m", "wordfreq", *args],
                              input=input, capture_output=True, check=False)

    def assert_path_error(self, code, out, err, path):
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1)
        self.assertTrue(err.startswith(f"wordfreq: error: {path}: "))

    def run_cli(self, argv, stdin=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(argv, stdin=stdin or io.StringIO(), stdout=stdout, stderr=stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def run_file(self, content, options=()):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
            return self.run_cli([str(path), *options])

    def test_file_counts_and_ranks_words(self):
        self.assertEqual(self.run_file('The, the THE. [apple] apple "banana"\nbanana\tcarrot'),
                         (0, "the 3\napple 2\nbanana 2\ncarrot 1\n", ""))

    def test_default_top_ten_and_explicit_limit(self):
        text = "l k j i h g f e d c b a"
        self.assertEqual(self.run_file(text),
                         (0, "a 1\nb 1\nc 1\nd 1\ne 1\nf 1\ng 1\nh 1\ni 1\nj 1\n", ""))
        self.assertEqual(self.run_file(text, ["--top", "2"]), (0, "a 1\nb 1\n", ""))
        self.assertEqual(self.run_file("a a", ["--top", "20"]), (0, "a 2\n", ""))

    def test_empty_and_punctuation_only_files(self):
        for text in ("", " \t\n,.!?[]'\"—_"):
            with self.subTest(text=text):
                self.assertEqual(self.run_file(text), (0, "", ""))

    def test_file_decoding_replaces_invalid_utf8(self):
        self.assertEqual(self.run_file(b"caf\xc3\xa9\xfftea"), (0, "café 1\ntea 1\n", ""))

    def test_module_runs_as_a_process(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_text("pear pear apple", encoding="utf-8")
            result = self.run_process(str(path))
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, b"pear 2\napple 1\n", b""))

    def test_contractions_normalise_apostrophes(self):
        self.assertEqual(self.run_file("don't don’t o'clock 'word' ’word’ a''b"),
                         (0, "don't 2\nword 2\na 1\nb 1\no'clock 1\n", ""))

    def test_dashes_underscores_digits_and_unicode(self):
        self.assertEqual(self.run_file("well-known word—word word–word foo_bar 2024 mp3 café Café CAFÉ naïve"),
                         (0, "word 4\ncafé 3\n2024 1\nbar 1\nfoo 1\nknown 1\nmp3 1\nnaïve 1\nwell 1\n", ""))

    def test_words_include_letters_and_decimal_digits_but_not_other_numbers(self):
        self.assertEqual(self.run_file("x²y ½ Ⅳ aⅣb ٣ mp3 café don't don’t"),
                         (0, "don't 2\na 1\nb 1\ncafé 1\nmp3 1\nx 1\ny 1\n٣ 1\n", ""))

    def test_stdin_and_top_limit(self):
        self.assertEqual(self.run_cli(["-"], io.StringIO("pear apple pear")),
                         (0, "pear 2\napple 1\n", ""))
        self.assertEqual(self.run_cli(["-", "--top", "1"], io.StringIO("pear apple pear")),
                         (0, "pear 2\n", ""))

    def test_unreadable_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            for path in (str(Path(directory) / "missing.txt"), directory):
                with self.subTest(path=path):
                    self.assert_path_error(*self.run_cli([path]), path)

    def test_usage_errors(self):
        for argv in (["-", "--top", "0"], ["-", "--top", "-3"],
                     ["-", "--top", "abc"], []):
            with self.subTest(argv=argv):
                self.assert_usage_error(argv)

    def assert_usage_error(self, argv):
        code, out, err = self.run_cli(argv)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("usage:", err)

    def test_help_describes_arguments(self):
        code, out, err = self.run_cli(["--help"])
        self.assertEqual((code, err), (0, ""))
        for phrase in ("file", "stdin", "--top", "10"):
            self.assertIn(phrase, out)

    def test_process_stdin_replaces_invalid_utf8(self):
        result = self.run_process("-", input=b"tea\xfftea")
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, b"tea 2\n", b""))

    def test_permission_error(self):
        with patch("builtins.open", side_effect=PermissionError(13, "Permission denied")):
            self.assertEqual(self.run_cli(["input.txt"]),
                             (2, "", "wordfreq: error: input.txt: Permission denied\n"))

    def test_read_error(self):
        input_file = mock_open()
        input_file.return_value.read.side_effect = OSError(5, "Input/output error")
        with patch("builtins.open", input_file):
            self.assertEqual(self.run_cli(["input.txt"]),
                             (2, "", "wordfreq: error: input.txt: Input/output error\n"))

    def test_missing_argument_does_not_read_stdin(self):
        class UnreadableInput(io.StringIO):
            def read(self, size: int | None = -1) -> str:
                raise AssertionError("stdin must not be read")
        code, out, err = self.run_cli([], UnreadableInput())
        self.assertEqual((code, out), (2, ""))
        self.assertIn("usage:", err)

    def test_missing_file_process_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "missing.txt")
            result = self.run_process(path)
        self.assert_path_error(result.returncode, result.stdout.decode(),
                               result.stderr.decode(), path)
