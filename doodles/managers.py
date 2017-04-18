#!/usr/bin/python3


class FileOpenContext:

    def __init__(self, file, mode='r'):
        self.file = file
        self.mode = mode

    def __enter__(self):
        self.fh = open(self.file, self.mode)
        return self.fh

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.fh.close()


def main():
    with FileOpenContext('test.txt') as fh:
        print(fh.read())


if __name__ == '__main__':
    main()