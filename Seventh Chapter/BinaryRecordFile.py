#!/usr/bin/python3

import os


_DELETED = b"\x01"
_OKAY = b"\x02"


class BinaryRecordFile:
    def __init__(self, filename, record_size, auto_flush=False):
        self.__record_size = record_size + 1
        mode = 'r+b' if os.path.exists(filename) else 'w+b'
        self.__fh = open(filename, mode=mode)
        self.auto_flush = auto_flush

    @property
    def record_size(self):
        return self.__record_size - 1

    @property
    def name(self):
        return self.__fh.name

    def auto_flush(self):
        self.__fh.flush()

    def close(self):
        self.__fh.close()

    def __setitem__(self, index, value):
        assert isinstance(value, (bytes, bytearray)), 'binary data needed'
        assert len(value) == self.record_size, 'invalid data size'
        self.__fh.seek(index * self.__record_size)
        self.__fh.write(_OKAY)
        self.__fh.write(value)
        if self.auto_flush:
            self.__fh.flush()

    def __len__(self):
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        return end // self.__record_size

    def __getitem__(self, index):
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state != _OKAY:
            return None
        return self.__fh.read(self.record_size)

    def __delitem__(self, index):
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state != _OKAY:
            return
        self.__fh.seek(index * self.__record_size)
        self.__fh.write(_DELETED)
        if self.auto_flush:
            self.__fh.flush()

    def undelete(self, index):
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        if state == _DELETED:
            self.__fh.seek(index * self.__record_size)
            self.__fh.write(_OKAY)
            if self.auto_flush:
                self.__fh.flush()
            return True
        return False

    def __seek_to_index(self, index):
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        position = index * self.__record_size
        if position >= end:
            raise IndexError('no item at index position {}'.format(index))
        self.__fh.seek(position)

    def inplace_compact(self):
        index = 0
        end = len(self)
        while index < end:
            self.__seek_to_index(index)
            state = self.__fh.read(1)
            if state != _OKAY:
                for next in range(index +1, end):
                    self.__seek_to_index(next)
                    state = self.__fh.read(1)
                    if state == _OKAY:
                        self[index] = self[next]
                        del self[next]
                        break
                else:
                    break
            index += 1
        self.__seek_to_index(0)
        if self.__fh.read(1) != _OKAY:
            self.__fh.truncate(0)
        else:
            limit = None
            for index in range(end-1, 0, -1):
                self.__seek_to_index(index)
                if self.__fh.read(1) != _OKAY:
                    limit = index
                else:
                    break
            if limit is not None:
                self.__fh.truncate(limit * self.__record_size)
        self.__fh.flush()

    def compact(self, keep_backup=False):
        compact_file = self.__fh.name + '.$$$'
        backup_file = self.__fh.name + '.bak'

        self.__fh.flush()
        self.__fh.seek(0)
        fh = open(compact_file, 'wb')
        while True:
            data = self.__fh.read(self.__record_size)
            if not data:
                break
            if data[:1] == _OKAY:
                fh.write(data)
        fh.close()
        self.__fh.close()

        os.rename(self.__fh.name, backup_file)
        os.rename(compact_file, self.__fh.name)

        if not keep_backup:
            os.remove(backup_file)
        self.__fh = open(self.__fh.name, 'r+b')



