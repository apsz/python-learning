#!/usr/bin/python3
# ~0.65 sec

import os
import argparse
import random


random.seed(1)


def read_file(file):
    try:
        with open(file) as fh:
            return fh.readlines()
    except (EnvironmentError, IOError, UnicodeDecodeError):
        return


def print_lines(file, lines):
    for lino, line in lines:
        print('{} {}: {:.80}'.format(file, lino, line))


def find_lines(text, word):
    lines = []
    for lino, line in enumerate(text, 1):
        line = line.strip()
        if word in line:
            lines.append((lino, line))
    return lines


def process_file(file, word):
    text = read_file(file)
    if text:
        found_lines = find_lines(text, word)
        if found_lines:
            print_lines(file, found_lines)


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
    if args.mode == 'f':
        for file in args.files:
            process_file(file, args.word)
    else:
        for dir in args.directories:
            if args.recursive:
                for root, _, files in os.walk(dir):
                    for file in files:
                        file = os.path.join(root, file)
                        process_file(file, args.word)
            else:
                for file in os.listdir(dir):
                    if os.path.isfile(file):
                        process_file(file, args.word)


if __name__ == '__main__':
    main()



