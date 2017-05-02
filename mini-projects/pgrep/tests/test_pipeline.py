#!/usr/bin/python3


import io
import sys
import functools
import unittest
import unittest.mock
import pgrep_pipeline


class ReplaceStandardOutput:

    def __init__(self):
        self._stdout_backup = sys.stdout

    def __enter__(self):
        sys.stdout = io.StringIO()
        return sys.stdout

    def __exit__(self, *ignore):
        sys.stdout = self._stdout_backup


def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        decorated = function(*args, **kwargs)
        next(decorated)
        return decorated
    return wrapper


@coroutine
def printer():
    while True:
        obj = (yield)
        print(obj)


class TestPGrepPipeline(unittest.TestCase):

    # get_text()
    @unittest.mock.patch('pgrep.pgrep_pipeline.open', return_value=io.StringIO('hello'))
    def test01_get_text_success(self, io_file):
        with ReplaceStandardOutput() as changed_stdout:
            pipeline = pgrep_pipeline.get_text(printer())
            pipeline.send('hello.txt')
            self.assertEqual(changed_stdout.getvalue().strip(), "(1, 'hello', 'hello.txt')")

    @unittest.mock.patch('pgrep.pgrep_pipeline.open', return_value=io.StringIO())
    def test02_get_text_empty_text_fail(self, io_file):
        with ReplaceStandardOutput() as changed_stdout:
            pipeline = pgrep_pipeline.get_text(printer())
            pipeline.send('hello.txt')
            self.assertEqual(changed_stdout.getvalue().strip(), '')

    # find_word()
    def test03_find_word_success(self):
        with ReplaceStandardOutput() as changed_stdout:
            pipeline = pgrep_pipeline.find_word(printer(), 'findme')
            pipeline.send((1, 'findme now', 'hello.txt'))
            self.assertEqual(changed_stdout.getvalue().strip(), "(1, 'findme now', 'hello.txt')")

    def test04_find_word_not_found_fail(self):
        with ReplaceStandardOutput() as changed_stdout:
            pipeline = pgrep_pipeline.find_word(printer(), 'findme')
            pipeline.send((1, 'cant find you', 'hello.txt'))
            self.assertEqual(changed_stdout.getvalue().strip(), '')

    def test05_find_word_invalid_arg_type_fail(self):
        pipeline = pgrep_pipeline.find_word(printer(), 'findme')
        with self.assertRaises(ValueError):
            pipeline.send([])
            pgrep_pipeline.find_word(printer(), 'findme')

    # print_line_and_file()
    def test06_print_line_and_file_success(self):
        pipeline = pgrep_pipeline.print_line_and_file()
        with ReplaceStandardOutput() as changed_stdout:
            pipeline.send((1, 'hello world', 'hello.txt'))
            self.assertEqual(changed_stdout.getvalue().strip(), 'hello.txt 1: hello world')

    def test07_print_line_and_file_invalid_arg_type_fail(self):
        pipeline = pgrep_pipeline.print_line_and_file()
        with self.assertRaises(ValueError):
            pipeline.send([])
            pgrep_pipeline.print_line_and_file()

    # integration - whole pipeline
    @unittest.mock.patch('pgrep.pgrep_pipeline.open', return_value=io.StringIO('want to findme'))
    def test08_integration_full_pipeline_success(self, *ignore):
        pipeline = pgrep_pipeline.get_text(pgrep_pipeline.find_word(
                      pgrep_pipeline.print_line_and_file(), 'findme'))
        with ReplaceStandardOutput() as changed_stdout:
            pipeline.send('hello.txt')
            self.assertEqual(changed_stdout.getvalue().strip(), 'hello.txt 1: want to findme')

    @unittest.mock.patch('pgrep.pgrep_pipeline.open', return_value=io.StringIO('cant findme'))
    def test09_integration_full_pipeline_no_match_fail(self, *ignore):
        pipeline = pgrep_pipeline.get_text(pgrep_pipeline.find_word(
                      pgrep_pipeline.print_line_and_file(), 'foundyou'))
        with ReplaceStandardOutput() as changed_stdout:
            pipeline.send('hello.txt')
            self.assertEqual(changed_stdout.getvalue().strip(), '')


if __name__ == '__main__':
    unittest.main()
