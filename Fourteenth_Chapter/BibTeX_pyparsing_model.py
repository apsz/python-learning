#!/usr/bin/python3


import sys
import re
from pyparsing import (Suppress, Word, Regex, QuotedString, OneOrMore,
                       delimitedList, ParseException, alphanums, alphas, nums)


""" BNF 

    BOOK ::= '@Book' '{' BOOK_ID '}'
          |  '@Book' '{' BOOK_ID ',' ATTR '}'
          |  '@Book' '{' BOOK_ID ',' ATTR_LIST '}'
    ATTR_LIST ::= '{' ATTR '}'
               |  '{' ATTR ',' ATTR_LIST '}'
    ATTR ::= KEY \s* = \s* VALUE
    VALUE ::= '"' TXT_VALUE '"'
           |      INT_VALUE
    KEY :: = [a-zA-Z]+\w*
    BOOK_ID ::= [^\s]+
    TXT_VALUE ::= [^\n"]+
    INT_VALUE ::= \d+

"""


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error while reading/accessing {}: {}'.format(file, file_err))
        sys.exit()


def py_parse(text):

    WHITESPACE = re.compile('\s+')
    books = {}
    keys_values = {}

    def normalize(tokens):
        return WHITESPACE.sub(' ', tokens[0])

    def add_key_value(tokens):
        keys_values[tokens.key] = tokens.value

    def add_book(tokens):
        books[tokens.book_id] = keys_values.copy()
        keys_values.clear()

    l_curly, r_curly, equals, comma = map(Suppress, '{}=,')
    book_ini = Suppress('@Book') + l_curly
    book_id = (Regex(r'[^\s,]+') + comma)('book_id')
    key = Word(alphanums, alphas)('key')
    value = (QuotedString('"', multiline=True).setParseAction(normalize) |
             Word(nums).setParseAction(lambda tokens: int(tokens[0])))('value')
    key_value = (key + equals + value).setParseAction(add_key_value)
    book_entry = book_ini + book_id + delimitedList(key_value) + r_curly
    book_entry.setParseAction(add_book)
    book_entries = OneOrMore(book_entry)

    try:
        book_entries.parseString(text, parseAll=True)
        return books
    except ParseException as parse_err:
        print('Error: ', parse_err)
        return {}


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 \
            or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.tex'.format(sys.argv[0]))
        sys.exit()

    file = sys.argv[1]
    text = get_text(file)
    books = py_parse(text)
    for k in books:
        print(k)
        for j in books[k]:
            print('\t{}: {}'.format(j, books[k][j]))


if __name__ == '__main__':
    main()