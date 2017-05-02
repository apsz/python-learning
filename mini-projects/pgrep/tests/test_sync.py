#!/usr/bin/python3


import sys
import io
import unittest
import unittest.mock
import pgrep_sync


class ReplaceStandardOutput:

    def __init__(self):
        self._stdout_backup = sys.stdout

    def __enter__(self):
        sys.stdout = io.StringIO()
        return sys.stdout

    def __exit__(self, *ignore):
        sys.stdout = self._stdout_backup


class TestPGrepSync(unittest.TestCase):

    # get_args()
    def test01_get_args_no_word_fail(self):
        with self.assertRaises(SystemExit):
            pgrep_sync.get_args()

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'f', 'test.txt'])
    def test02_get_args_filemode_one_path_success(self):
        self.assertEqual(pgrep_sync.get_args().word, 'word')
        self.assertEqual(pgrep_sync.get_args().files, ['test.txt'])

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'f', 'test.txt', 'test2.txt'])
    def test03_get_args_filemode_multiple_paths_success(self):
        self.assertEqual(pgrep_sync.get_args().word, 'word')
        self.assertEqual(pgrep_sync.get_args().files, ['test.txt', 'test2.txt'])

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'f'])
    def test04_get_args_filemode_no_path_fail(self):
        with self.assertRaises(SystemExit):
            pgrep_sync.get_args()

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'f', 'test.txt', '-r'])
    def test05_get_args_filemode_set_recursive_fail(self):
        with self.assertRaises(SystemExit):
            pgrep_sync.get_args()

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'd', '.'])
    def test06_get_args_dirmode_one_dir_success(self):
        self.assertEqual(pgrep_sync.get_args().word, 'word')
        self.assertEqual(pgrep_sync.get_args().directories, ['.'])

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'd', '.', '../'])
    def test07_get_args_dirmode_multiple_dirs_success(self):
        self.assertEqual(pgrep_sync.get_args().word, 'word')
        self.assertEqual(pgrep_sync.get_args().directories, ['.', '../'])

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'd'])
    def test08_get_args_dirmode_no_dir_fail(self):
        with self.assertRaises(SystemExit):
            pgrep_sync.get_args()

    @unittest.mock.patch('sys.argv', ['test_sync.py', 'word', 'd', '.', '-r'])
    def test07_get_args_dirmode_set_recursive_success(self):
        self.assertEqual(pgrep_sync.get_args().word, 'word')
        self.assertEqual(pgrep_sync.get_args().directories, ['.'])
        self.assertEqual(pgrep_sync.get_args().recursive, True)

    # read_file()
    @unittest.mock.patch('pgrep.pgrep_sync.open', return_value=io.StringIO('hello\nworld'))
    def test08_read_file_success(self, fl):
        self.assertListEqual(pgrep_sync.read_file(fl), ['hello\n', 'world'])

    @unittest.mock.patch('pgrep.pgrep_sync.open', return_value=io.StringIO())
    def test09_read_file_empty_file_fail(self, fl):
        self.assertFalse(pgrep_sync.read_file(fl))

    # print_lines()
    def test10_print_lines_success(self):
        with ReplaceStandardOutput() as changed_stdout:
            pgrep_sync.print_lines('test.txt', [(1, 'line1')])
            self.assertEqual(changed_stdout.getvalue().strip(), 'test.txt 1: line1')

    def test11_print_lines_wrong_type_fail(self):
        with self.assertRaises(ValueError):
            pgrep_sync.print_lines('test.txt', ['not a tuple'])

    # find_lines()
    def test12_find_lines_match_found_success(self):
        self.assertEqual(pgrep_sync.find_lines(['hello\n', 'world'], 'world'), [(2, 'world')])

    def test13_find_lines_nothing_found_fail(self):
        self.assertEqual(pgrep_sync.find_lines(['hello\n', 'world'], 'findme'), [])

    def test14_find_lines_empty_text_fail(self):
        with self.assertRaises(TypeError):
            pgrep_sync.find_lines('findme', [])

    # process_file()
    @unittest.mock.patch('pgrep.pgrep_sync.read_file', return_value='not empty')
    @unittest.mock.patch('pgrep.pgrep_sync.find_lines', return_value=[(1, 'line1')])
    def test15_process_file_success(self, *ignore):
        with ReplaceStandardOutput() as changed_stdout:
            pgrep_sync.process_file('test.txt', 'word')
            self.assertEqual(changed_stdout.getvalue().strip(), 'test.txt 1: line1')

    @unittest.mock.patch('pgrep.pgrep_sync.read_file', return_value=[])
    def test16_process_file_empty_text_fail(self, *ignore):
        self.assertFalse(pgrep_sync.process_file('test.txt', 'word'))

    @unittest.mock.patch('pgrep.pgrep_sync.read_file', return_value='not empty')
    @unittest.mock.patch('pgrep.pgrep_sync.find_lines', return_value=[])
    def test17_process_file_lines_not_found_fail(self, *ignore):
        self.assertFalse(pgrep_sync.process_file('test.txt', 'word'))


if __name__ == '__main__':
    unittest.main()
