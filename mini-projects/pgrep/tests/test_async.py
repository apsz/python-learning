#!/usr/bin/python3

import io
import sys
import asyncio
import unittest
import unittest.mock
import pgrep_async


class ReplaceStandardOutput:

    def __init__(self):
        self._stdout_backup = sys.stdout

    def __enter__(self):
        sys.stdout = io.StringIO()
        return sys.stdout

    def __exit__(self, *ignore):
        sys.stdout = self._stdout_backup


async def put_to_queue(queue, item):
    await queue.put(item)
    await queue.put(None)


class TestPGrepAsync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    # read_file()
    @unittest.mock.patch('pgrep.pgrep_async.open', return_value=io.StringIO('hello\nworld'))
    def test01_read_file_success(self, *ignore):
        self.assertListEqual(self.loop.run_until_complete(pgrep_async.read_file('hello.txt')),
                             ['hello\n', 'world'])

    @unittest.mock.patch('pgrep.pgrep_async.open', return_value=io.StringIO())
    def test02_read_file_empty_file_fail(self, *ignore):
        self.assertListEqual(self.loop.run_until_complete(pgrep_async.read_file('hello.txt')), [])

    # print_lines()
    def test03_print_lines_success(self):
        with ReplaceStandardOutput() as changed_stdout:
            self.loop.run_until_complete(pgrep_async.print_lines('hello.txt', [(1, 'text line')]))
            self.assertEqual(changed_stdout.getvalue().strip(), 'hello.txt 1: text line')

    def test04_print_lines_empty_lines_fail(self):
        with ReplaceStandardOutput() as changed_stdout:
            self.loop.run_until_complete(pgrep_async.print_lines('hello.txt', []))
            self.assertEqual(changed_stdout.getvalue().strip(), '')

    def test05_print_lines_invalid_arg_fail(self):
        with self.assertRaises(ValueError):
            self.loop.run_until_complete(pgrep_async.print_lines('hello.txt', 'not a tuple'))

    # find_lines()
    def test06_find_lines_success(self):
        self.assertListEqual(self.loop.run_until_complete(
            pgrep_async.find_lines(['first line with findme',
                'second line with findme', 'line without'], 'findme')),
                [(1, 'first line with findme'), (2, 'second line with findme')])

    def test07_find_lines_no_matching_lines_fail(self):
        self.assertListEqual(self.loop.run_until_complete(
            pgrep_async.find_lines(['first line with findme',
                'second line with findme', 'line without'], 'cantfindthis')), [])

    def test08_find_lines_empty_text_fail(self):
        self.assertListEqual(self.loop.run_until_complete(
            pgrep_async.find_lines('', 'cantfindthis')), [])

    # process_file() functional
    @unittest.mock.patch('pgrep.pgrep_async.open', return_value=io.StringIO('want to findme'))
    def test09_process_file_success(self, fl):
        queue = asyncio.Queue()
        with ReplaceStandardOutput() as changed_stdout:
            producer = put_to_queue(queue, fl)
            consumer = pgrep_async.process_file(queue, self.loop, 'findme')
            self.loop.run_until_complete(asyncio.gather(producer, consumer))
            self.assertEqual(changed_stdout.getvalue().strip()[-17:], '1: want to findme')


    @unittest.mock.patch('pgrep.pgrep_async.open', return_value=io.StringIO('want to findme'))
    def test09_process_file_no_match_fail(self, fl):
        queue = asyncio.Queue()
        with ReplaceStandardOutput() as changed_stdout:
            producer = put_to_queue(queue, fl)
            consumer = pgrep_async.process_file(queue, self.loop, 'cannotfindanything')
            self.loop.run_until_complete(asyncio.gather(producer, consumer))
            self.assertEqual(changed_stdout.getvalue().strip()[-17:], '')


if __name__ == '__main__':
    unittest.main()