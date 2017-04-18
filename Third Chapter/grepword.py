#!/usr/bin/python3

import sys


def main():
    if len(sys.argv) < 2:
        print('usage: {} <searched word> <file1> <file2> <fileN>'.format(sys.argv[0]))
        sys.exit()

    searched = sys.argv[1]
    for file in sys.argv[2:]:
        for line_number, line in enumerate(open(file),1):
            if searched.lower() in line.lower():
                print('{file} {line_number} '
                      '{searched:.40}'.format(**locals()))


main()