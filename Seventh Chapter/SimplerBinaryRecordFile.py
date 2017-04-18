#!/usr/bin/python3

import os
import struct

class BinaryRecordFile:

    def __init__(self, filename, record_size, auto_flush=False):
        mode = 'w+b' if not os.path.exists(filename) else 'r+b'
        self.__fh = open(filename, mode=mode)
        self.auto_flush = auto_flush
        self.__record_size = record_size

    @property
    def filename(self):
        return self.__fh.name

    @property
    def record_size(self):
        return self.__record_size

    def auto_flush(self):
        self.__fh.flush()

    def close(self):
        self.__fh.close()

    def __len__(self):
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        return end // self.record_size

    def append(self, record):
        assert isinstance(record, (bytes, bytearray)), 'binary data required'
        assert len(record) == self.record_size, \
            'record must be exactly {} bytes'.format(self.record_size)
        self.__fh.seek(0, os.SEEK_END)
        self.__fh.write(record)
        if self.auto_flush:
            self.__fh.flush()

    def __getitem__(self, index):
        self.__seek_to_index(index)
        return self.__fh.read(self.record_size)

    def __delitem__(self, index):
        for idx in range(index, len(self)-1):
            self[idx] = self[idx + 1]
        self.__fh.truncate(self.record_size * (len(self))-1)
        self.__fh.flush()

    def __setitem__(self, index, record):
        assert isinstance(record, (bytes, bytearray)), 'binary data required'
        assert len(record) == self.record_size, \
            'record must be exactly {} bytes'.format(self.record_size)
        self.__seek_to_index(index)
        self.__fh.write(record)
        if self.auto_flush:
            self.__fh.flush()

    def __seek_to_index(self, index):
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        offset = index * self.record_size
        if offset >= end:
            raise IndexError('index out of range')
        self.__fh.seek(offset)

