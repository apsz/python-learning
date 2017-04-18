#!/usr/bin/python3

import os

_DELETED = b"\x01"
_OKAY = b"\x02"


class BinaryRecordFile:

    def __int__(self, filename, record_size, auto_flush=False):
        self.__record_size = record_size + 1
        mode = 'w+b' if not os.path.exists(filename) else "r+b"
        self.__fh = open(filename, mode=mode)
        self.auto_flush = auto_flush

    @property
    def filename(self):
        return self.__fh.name

    @property
    def record_size(self):
        return self.__record_size - 1

    def auto_flush(self):
        self.__fh.flush()

    def close(self):
        self.__fh.close()

    def __len__(self):
        if self.auto_flush:
            self.__fh.flush()
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        return end // self.__record_size

    def __setitem__(self, index, value):
        assert isinstance(value, (bytearray, bytes)), \
            'binary data required'
        assert len(value) == self.record_size, \
            'invalid data size, must be {}'.format(self.record_size)
        self.__fh.seek(index * self.__record_size)
        self.__fh.write(_OKAY)
        self.__fh.write(value)
        if self.auto_flush:
            self.__fh.flush()
        return True

    def __getitem__(self, index):
        self.__seek_to_index(index)
        if self.__fh.read(1) != _OKAY:
            return None
        return self.__fh.read(self.record_size)

    def __delitem__(self, index):
        self.__seek_to_index(index)
        if self.__fh.read(1) == _OKAY:
            self.__fh.seek(index * self.__record_size)
            self.__fh.write(_DELETED)
            if self.auto_flush:
                self.__fh.flush()
            return True
        return False

    def undelete(self, index):
        self.__seek_to_index(index)
        if self.__fh.read(1) == _DELETED:
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
        offset = index * self.__record_size
        if offset >= end:
            raise IndexError('index out of range')
        self.__fh.seek(offset)

    def compact(self, backup=False):
        compact_file = self.filename + '.$$$'
        backup_file = self.filename + '.bak'
        self.__fh.flush()
        self.__fh.seek(0)

        fh = None
        try:
            fh = open(compact_file, 'wb')
            for index in range(len(self)):
                data = self[index]
                if data[:1] == _OKAY:
                    fh.write(data)
        except (EnvironmentError, IOError) as file_err:
            print('Error while saving file: {}'.format(file_err))
            return False
        finally:
            if fh:
                fh.close()
                self.__fh.close()

        os.rename(self.filename, backup_file)
        os.rename(compact_file, self.__fh.name)

        if not backup:
            os.remove(backup_file)
        self.__fh = open(self.__fh.name, 'r+b')

    def compact_inplace(self):
        for index in range(len(self)):
            data = self[index]
            if data[:1] != _OKAY:
                for offset in range(index + 1, len(self)):
                    new_data = self[offset]
                    if new_data[:1] == _OKAY:
                        self[index] = self[offset]
                        del self[offset]
                        break
                else:
                    break
        self.__fh.seek(0)

        if self.__fh.read(1) != _OKAY:
            self.__fh.truncate(0)
        else:
            limit = 0
            for index in range(len(self)-1, 0, -1):
                if self[index][0] != _OKAY:
                    limit = index
                else:
                    break
            if limit > 0:
                self.__fh.truncate(limit * self.__record_size)
        self.__fh.flush()










