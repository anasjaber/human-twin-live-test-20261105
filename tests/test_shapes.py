from tests.support import CsvFileCase


class ShapeTests(CsvFileCase):
    def test_quoted_commas_and_newlines(self):
        self.assertEqual(self.run_csv('"value,amount","multi\nline",note\n'
                                      '2,4,"hello,\nworld"\n6,8,text\n'),
                         (0, 'value,amount 2 2 6 4.00\nmulti\nline 2 4 8 6.00\n', ''))

    def test_bom_is_removed_from_first_header(self):
        self.assertEqual(self.run_csv('\ufeffamount\n7\n'), (0, 'amount 1 7 7 7.00\n', ''))

    def test_short_rows_treat_missing_cells_as_blank(self):
        self.assertEqual(self.run_csv('a,b\n1,6\n3\n'),
                         (0, 'a 2 1 3 2.00\nb 1 6 6 6.00\n', ''))

    def test_extra_cells_are_ignored(self):
        self.assertEqual(self.run_csv('a\n1,999\n3,1000,2000\n'),
                         (0, 'a 2 1 3 2.00\n', ''))

    def test_duplicate_names_remain_separate_columns(self):
        self.assertEqual(self.run_csv('a,a\n1,10\n3,20\n'),
                         (0, 'a 2 1 3 2.00\na 2 10 20 15.00\n', ''))

    def test_empty_and_header_only_inputs(self):
        for data in ('', 'a,b\n'):
            with self.subTest(data=data):
                self.assertEqual(self.run_csv(data), (0, '', ''))
