import contextlib
import io
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from csvstats import main
from tests.support import CliCase


class ShellTests(CliCase):
    def test_stdin_summary(self):
        self.assertEqual(self.invoke(['-'], 'age,score\n30,88.5\n,92\n25,n/a\n'),
                         (0, 'age 2 25 30 27.50\nscore 2 88.5 92 90.25\n', ''))

    def test_missing_file_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'missing.csv')
            self.assert_error(self.invoke([path]), path)

    def test_os_error_reason_does_not_repeat_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'missing.csv')
            code, output, error = self.invoke([path])
            self.assertEqual((code, output), (2, ''))
            self.assertEqual(error.count(path), 1)

    def test_directory_reports_error(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assert_error(self.invoke([directory]), directory)

    def test_invalid_utf8_produces_no_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.csv'
            path.write_bytes(b'n\n1\n' + b'2\n' * 10000 + b'\xff')
            self.assert_error(self.invoke([str(path)]), str(path))

    def test_csv_parse_error_produces_no_partial_output(self):
        self.assert_error(self.invoke(['-'], 'n\n1\n' + '2' * 200000 + '\n'), '-')

    def test_permission_denied_reports_error(self):
        # File opening is an OS boundary; injecting this failure works as root too.
        with patch('builtins.open', side_effect=PermissionError('permission denied')):
            self.assert_error(self.invoke(['private.csv']), 'private.csv')

    def test_stdin_read_failure_reports_error(self):
        class BrokenInput(io.StringIO):
            def __next__(self):
                raise OSError('input read failed')

        self.assert_error(self.invoke(['-'], BrokenInput()), '-')

    def test_usage_errors(self):
        for argv in ([], ['one.csv', 'two.csv']):
            with self.subTest(argv=argv):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
                    self.invoke(argv)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('usage:', stderr.getvalue())

    def test_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
            self.invoke(['--help'])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn('file', stdout.getvalue())
        self.assertIn('- for stdin', stdout.getvalue())

    def test_default_streams(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch('sys.stdin', io.StringIO('n\n4\n')):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main(['-'])
        self.assertEqual((code, stdout.getvalue(), stderr.getvalue()),
                         (0, 'n 1 4 4 4.00\n', ''))

    def test_module_smoke(self):
        result = subprocess.run([sys.executable, '-m', 'csvstats', '-'],
                                input='n\n2\n4\n', text=True, capture_output=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, 'n 2 2 4 3.00\n', ''))
