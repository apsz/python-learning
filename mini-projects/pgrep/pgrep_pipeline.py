#!/usr/bin/python3
# ~0.7 sec

import os
import argparse
import functools
import random


random.seed(1)


def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        decorated = function(*args, **kwargs)
        next(decorated)
        return decorated
    return wrapper


@coroutine
def get_text(receiver):
    while True:
        file = (yield)
        try:
            with open(file) as fh:
                for lino, line in enumerate(fh, 1):
                    if line:
                        receiver.send((lino, line.strip(), file))
        except (EnvironmentError, IOError, UnicodeError):
            pass


@coroutine
def find_word(receiver, word):
    while True:
        lino, line, file = (yield)
        if word in line:
            receiver.send((lino, line, file))


@coroutine
def print_line_and_file():
    while True:
        lino, line, file = (yield)
        print('{} {}: {:.80}'.format(file, lino, line))


def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('word', type=str, help='Word to look for.')
    subparsers = parser.add_subparsers(help='FGrep modes', dest='mode')
    file_parser = subparsers.add_parser('f', help=('Use file mode.\n\t'
                                                   'Usage: f <file1> <file2> <fileN>'))
    file_parser.add_argument('files', type=str, nargs='+')
    directory_parser = subparsers.add_parser('d', help=('Use directory mode.\n\t'
                                                        'Usage: d [-r] <dir1> <dir2> <dirN>\n\t'
                                                        'Optional: -r '
                                                        '(recursively search given directories).'))
    directory_parser.add_argument('-r', '--recursive', action='store_true')
    directory_parser.add_argument('directories', type=str, nargs='+')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    pipeline = get_text(find_word(print_line_and_file(), args.word))

    if args.mode == 'f':
        for file in args.files:
            pipeline.send(file)
    else:
        for dir in args.directories:
            if args.recursive:
                for root, _, files in os.walk(dir):
                    for file in files:
                        pipeline.send(os.path.join(root, file))
            else:
                for file in os.listdir(dir):
                    if os.path.isfile(file):
                        pipeline.send(file)
    pipeline.close()


if __name__ == '__main__':
    main()
