from tests.support import CsvFileCase


class StatsTests(CsvFileCase):
    def test_spec_example_in_header_order(self):
        self.assertEqual(self.run_csv(
            'name,age,score,city\nalice,30,88.5,Paris\nbob,,92,Berlin\ncarol,25,n/a,Rome\n'
        ), (0, 'age 2 25 30 27.50\nscore 2 88.5 92 90.25\n', ''))

    def test_numeric_rules_and_formatting(self):
        self.assertEqual(self.run_csv(
            'mixed,rounded,whole,text,blank\n'
            '-3,1.234,2,hello,\n'
            '1e3,1.236,4,world,\n'
            ' 42 ,,,n/a,\n'
            '+5,,,word,\n'
            '1_000,,,word,\n'
            'nan,,,word,\ninf,,,word,\n-inf,,,word,\n'
            'n/a,,,word,\n-,,,word,\n ,,,word,\n'
        ), (0, 'mixed 5 -3 1000 408.80\nrounded 2 1.234 1.236 1.23\n'
                'whole 2 2 4 3.00\n', ''))

    def test_no_numeric_columns(self):
        self.assertEqual(self.run_csv('name,blank\nalice,\nbob, \n'), (0, '', ''))

    def test_sum_preserves_small_values_during_cancellation(self):
        self.assertEqual(self.run_csv('n\n1e16\n1\n-1e16\n'),
                         (0, 'n 3 -10000000000000000 10000000000000000 0.33\n', ''))

    def test_overflow_keeps_other_columns_and_returns_success(self):
        for value, expected in (('1e308', 'inf'), ('-1e308', '-inf')):
            with self.subTest(value=value):
                result = self.run_csv(f'large,small\n{value},1\n{value},2\n')
                self.assertEqual(result[0], 0)
                self.assertEqual(result[2], '')
                self.assertEqual(result[1].splitlines()[0].split()[-1], expected)
                self.assertEqual(result[1].splitlines()[1], 'small 2 1 2 1.50')
