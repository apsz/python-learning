#!/usr/bin/python3

import sys
import unicodedata


def main():
    name = None
    if len(sys.argv) > 1:
        name = sys.argv[1].lower()

    start = ord(' ')
    end = sys.maxunicode

    print('{:^7} {:^5} {:^3} {:^40}'.format('decimal', 'hex', 'chr', 'name'))
    print('{0:-^7} {0:-^5} {0:-^3} {0:-^40}'.format('-'))
    print_unicode_data(start, end, name)


def print_unicode_data(start, end, name):
    while start < end:
        uni_name = unicodedata.name(chr(start), "unknown")
        if name is None or name in uni_name.lower():
            print('{0: >7} {0: >#5x} {1: ^3} {2: <40}'.format(start, chr(start), uni_name.title()))
        start += 1


main()


