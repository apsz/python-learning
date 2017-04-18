#!/usr/bin/python3


import unittest
from . import Atomic


class TestAtomic(unittest.TestCase):

    def setUp(self):
        self.original_list = list(range(10))
        self.original_set = set(list(range(10)))
        self.original_dict = dict.fromkeys('ABCDEFG', 0)

    def test_list_succeed(self):
        items = self.original_list[:]
        with Atomic.Atomic(items) as atomic:
            atomic.append(1999)
            atomic.insert(2, -915)
            del atomic[5]
            atomic[4] = -782
            atomic.insert(0, -9)
        self.assertListEqual(items,
                          [-9, 0, 1, -915, 2, -782,
                           5, 6, 7, 8, 9, 1999])

    def test_list_fail(self):
        items = self.original_list[:]
        with self.assertRaises(AttributeError):
            with Atomic.Atomic(items) as atomic:
                atomic.append(1999)
                atomic.insert(2, -915)
                del atomic[5]
                atomic[4] = -782
                atomic.poop()  # Typo
        self.assertListEqual(items, self.original_list)

    def test_set_succeed(self):
        test_set = set(self.original_set)
        with Atomic.Atomic(test_set) as atomic:
            atomic.add(20)
            atomic.add(10)
            atomic.discard(10)
            atomic.discard(0)
            atomic.add(20)
        self.assertSetEqual(test_set, {1, 2, 3, 4, 5, 6,
                                       7, 8, 9, 20})

    def test_set_fail(self):
        test_set = set(self.original_set)
        with self.assertRaises(AttributeError):
            with Atomic.Atomic(test_set) as atomic:
                atomic.add(20)
                atomic.add(10)
                atomic.discard(10)
                atomic.discar(0)
        self.assertSetEqual(test_set, self.original_set)

    def test_dict_succeed(self):
        test_dict = dict(self.original_dict)
        with Atomic.Atomic(test_dict) as atomic:
            del atomic['A']
            atomic['C'] = 10
            atomic['Z'] = 20
            del atomic['B']
        self.assertDictEqual(test_dict, {'C': 10, 'D': 0, 'E': 0,
                                         'F': 0, 'G': 0, 'Z': 20})

    def test_dict_fail(self):
        test_dict = dict(self.original_dict)
        with self.assertRaises(KeyError):
            with Atomic.Atomic(test_dict) as atomic:
                del atomic['Z']
                atomic['C'] = 10
                atomic['Z'] = 20
        self.assertDictEqual(test_dict, self.original_dict)


if __name__ == '__main__':
    unittest.main()
