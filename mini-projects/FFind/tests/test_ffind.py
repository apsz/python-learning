#!/usr/bin/python3


import asyncio
import argparse
import unittest
import unittest.mock
import ffind


class TestFFindSync(unittest.TestCase):

    def test01_get_bytes_int_success(self):
        self.assertEqual(ffind.get_bytes('20'), 20)

    def test02_get_bytes_string_m_success(self):
        self.assertEqual(ffind.get_bytes('1m'), 1024**2)

    def test03_get_bytes_string_k_success(self):
        self.assertEqual(ffind.get_bytes('20k'), 1024*20)

    def test04_get_bytes_string_space_format_success(self):
        self.assertEqual(ffind.get_bytes('20 k'), 1024 * 20)

    def test05_get_bytes_wrong_format_fail(self):
        with self.assertRaises(ValueError):
            ffind.get_bytes('2.0')

    @unittest.mock.patch('sys.argv', ['ffind.py', '-p', '.'])
    def test06_get_args_default_path_success(self, *ignore):
        self.assertEqual(ffind.get_args(),
                         argparse.Namespace(bigger=None, days=None, output=None,
                                            path='.', smaller=None, suffix=None))

    def test07_get_args_default_no_path_fail(self):
        with self.assertRaises(SystemExit):
            ffind.get_args()

    @unittest.mock.patch('sys.argv', ['ffind.py', '-p', '.', '-b', '10m', '-s', '20m'])
    def test08_get_args_bigger_smaller_fail(self):
        with self.assertRaises(SystemExit):
            ffind.get_args()

    @unittest.mock.patch('sys.argv', ['ffind.py', '-p', '.', '-d', '2'])
    def test09_get_args_days_conversion_success(self):
        self.assertTrue(isinstance(ffind.get_args().days, float))

    @unittest.mock.patch('sys.argv', ['ffind.py', '-p', '.', '-u', '.py', '.rb'])
    def test10_get_args_multiple_suffixes_success(self):
        self.assertListEqual(ffind.get_args().suffix, ['.py', '.rb'])

    @unittest.mock.patch('sys.argv', ['ffind.py', '-p', '.', '-u', '.py', '.rb'])
    def test10_get_args_multiple_suffixes_success(self):
        self.assertListEqual(ffind.get_args().suffix, ['.py', '.rb'])


class TestFFindAsync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    def test01_match_file_size_success(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_size('test')), 'test')

    @unittest.mock.patch('ffind.os')
    def test02_match_file_size_smaller_success(self, os_mock):
        os_mock.st_size = 9
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_size(['test', os_mock],
            smaller=1024))[0], 'test')

    @unittest.mock.patch('ffind.os')
    def test03_match_file_size_smaller_fail(self, os_mock):
        os_mock.st_size = 2024
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_size(['test', os_mock],
            smaller=1024)), None)

    @unittest.mock.patch('ffind.os')
    def test04_match_file_size_bigger_success(self, os_mock):
        os_mock.st_size = 2041
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_size(['test', os_mock],
            bigger=1024))[0], 'test')

    @unittest.mock.patch('ffind.os')
    def test05_match_file_size_bigger_fail(self, os_mock):
        os_mock.st_size = 9
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_size(['test', os_mock],
            bigger=1024)), None)

    def test06_match_file_date_empty_args_success(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_date('test')), 'test')

    @unittest.mock.patch('ffind.os')
    def test07_match_file_date_success(self, os_mock):
        os_mock.st_mtime = 1337
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_date(['test', os_mock],
            date=1336))[0], 'test')

    @unittest.mock.patch('ffind.os')
    def test08_match_file_date_fail(self, os_mock):
        os_mock.st_mtime = 1336
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_date(['test', os_mock],
            date=1337)), None)

    def test09_match_file_suffix_empty_success(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_suffix('test', [])), 'test')

    def test10_match_file_suffix_single_success(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_suffix(['test.py', None], ['.py'])),
                                                                              ['test.py', None])

    def test11_match_file_suffix_multiple_success(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_suffix(['test.rb', None], ['.py', '.rb'])),
                                                                              ['test.rb', None])

    def test12_match_file_suffix_fail(self):
        self.assertEqual(self.loop.run_until_complete(ffind.match_file_suffix(['test.rb', None], ['.py'])),
                                                                              None)


if __name__ == '__main__':
    unittest.main()
