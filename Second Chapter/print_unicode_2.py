#!/usr/bin/python3

import sys
import unicodedata


def main():
    names = []
    if len(sys.argv) > 1:
        names = sys.argv[1:]

    start = ord(' ')
    end = sys.maxunicode

    print('{:^7} {:^5} {:^3} {:^40}'.format('decimal', 'hex', 'chr', 'name'))
    print('{0:-^7} {0:-^5} {0:-^3} {0:-^40}'.format('-'))
    print_unicode_data(start, end, names)


def print_unicode_data(start, end, names):
    while start < end:
        uni_name = unicodedata.name(chr(start), "unknown").lower()
        found = True
        if names:
            for name in names:
                if name.lower() not in uni_name:
                    found = False
        if not names or found:
            print('{0: >7} {0: >#5x} {1: ^3} {2: <40}'.format(start, chr(start), uni_name.title()))
        start += 1


main()


