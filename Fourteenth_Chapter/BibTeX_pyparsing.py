#!/usr/bin/python3


import sys
import re
import collections
from pyparsing import Suppress, Word, Regex, QuotedString, OneOrMore, delimitedList, ParseException, alphanums, nums


""" BNF 

    BOOK ::= '@Book' '{' BOOK_ID '}'
          |  '@Book' '{' BOOK_ID ',' ATTR '}'
          |  '@Book' '{' BOOK_ID ',' ATTR_LIST '}'
    ATTR_LIST ::= '{' ATTR '}'
               |  '{' ATTR ',' ATTR_LIST '}'
    ATTR ::= KEY \s* = \s* VALUE
    VALUE ::= '"' TXT_VALUE '"'
           |      INT_VALUE
    KEY :: = [a-zA-Z]\w*
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


def ply_parse(text):

    def set_book_key(tokens):
        nonlocal current_key
        current_key = tokens.book_id[0]

    def add_book_attr(tokens):
        key, value = tokens[0], tokens[1]
        print(key, value)
        parsed_books[current_key][key.strip()] = value.strip()

    parsed_books = collections.defaultdict(dict)
    current_key = ''

    l_curly, r_curly, equals, comma = map(Suppress, '{}=,')
    book_id = (Suppress('@Book{') + Regex(r'[^\s,]+') + comma)('book_id')
    book_id.addParseAction(set_book_key)
    key_value = Word(alphanums) + equals + (QuotedString('"') | Word(nums))
    key_value.addParseAction(add_book_attr)
    books = OneOrMore(book_id + delimitedList(key_value) + r_curly)

    text = re.sub('\s+', ' ', text)
    try:
        books.parseString(text)
        return parsed_books
    except ParseException as parse_err:
        print('Error: {}'.format(parse_err))
        return {}


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.tex'.format(sys.argv[0]))
        sys.exit()

    file = sys.argv[1]
    text = get_text(file)
    books = ply_parse(text)
    print(books)
    for k in books:
        print(k)
        for j in books[k]:
            print('\t{}: {}'.format(j, books[k][j]))


if __name__ == '__main__':
    main()