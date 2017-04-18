#!/usr/bin/python3

import collections
import copy


class Atomic:

    def __init__(self, mutable_sequence, shallow_copy=True):
        assert isinstance(mutable_sequence, (collections.MutableMapping,
                                             collections.MutableSequence,
                                             collections.MutableSet)), \
            'argument must be a mutable sequence (set, list or dict or subclass)'
        self.original = mutable_sequence
        self.copy = copy.copy if shallow_copy else copy.deepcopy

    def __enter__(self):
        self.__modified = self.copy(self.original)
        return self.__modified

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            if isinstance(self.__modified, collections.MutableSequence):
                self.original[:] = self.__modified
            elif isinstance(self.__modified, (collections.MutableMapping,
                                                collections.MutableSet)):
                self.original.clear()
                self.original.update(self.__modified)