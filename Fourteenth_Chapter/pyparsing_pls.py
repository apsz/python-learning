#!/usr/bin/python


import sys
from pyparsing import (Word, CharsNotIn, Suppress, restOfLine,
                       OneOrMore, Optional, alphanums, ParseException)


def pyparse_pls(file, lowercase_keys=False):

    def accumulate(tokens):
        key, value = tokens
        key = key.lower() if lowercase_keys else key
        keys_values[key] = value

    keys_values = {}
    left_bracket, right_bracket, equal_sign = map(Suppress, '[]=')
    ini_line = left_bracket + CharsNotIn(']') + right_bracket
    key_value = Word(alphanums) + equal_sign + restOfLine
    key_value.addParseAction(accumulate)
    comment = '#' + restOfLine
    parser = Optional(ini_line) + OneOrMore(key_value)
    parser.ignore(comment)

    try:
        parser.parseFile(file)
    except ParseException as parse_err:
        print('Parsing error: {}', parse_err)
        return {}
    return keys_values


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 \
            or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.pls'.format(sys.argv[0]))
        sys.exit()

    parsed_keys_values = pyparse_pls(sys.argv[1])
    return parsed_keys_values


if __name__ == '__main__':
    print(main())