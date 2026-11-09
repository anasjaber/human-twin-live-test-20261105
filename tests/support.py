import io
import tempfile
import unittest
from pathlib import Path

from csvstats import main


class CliCase(unittest.TestCase):
    def invoke(self, argv, source=''):
        stdin = io.StringIO(source) if isinstance(source, str) else source
        stdout, stderr = io.StringIO(), io.StringIO()
        code = main(argv, stdin, stdout, stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_error(self, result, file):
        code, output, error = result
        self.assertEqual((code, output), (2, ''))
        self.assertTrue(error.startswith(f'csvstats: error: {file}: '), error)
        self.assertTrue(error.endswith('\n'))


class CsvFileCase(CliCase):
    def run_csv(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_text(data, encoding='utf-8', newline='')
            return self.invoke([str(path)])
