#!/usr/bin/python3


import sys
import re
import ply.lex
import collections


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


class ParseException(Exception): pass


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error while reading/accessing {}: {}'.format(file, file_err))
        sys.exit()


def ply_parse(text):

    tokens = ('BOOK_ID', 'KEY_VALUE')

    t_ignore = ' \t\n'
    t_BOOK_ID = r'@Book{[^,\s]+,'
    t_KEY_VALUE = r'[a-zA-Z]+\w+\s*=\s*(\d+|"[^"]+")+\s?(}|,)'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        new_line_idx = line.find('\n')
        line = line if new_line_idx == -1 else line[:new_line_idx]
        print('Error on line: {}: {}'.format(t.lexer.lineno, line))

    books = collections.defaultdict(collections.OrderedDict)
    current_book_key = None

    lexer = ply.lex.lex()
    text = re.sub(r'[\s]+', ' ', text)
    try:
        lexer.input(text)
        for token in lexer:
            if token.type == 'BOOK_ID':
                current_book_key = token.value[len('@Book{'):-1]
            elif token.type == 'KEY_VALUE':
                key, value = token.value.split('=')
                books[current_book_key][key.strip()] = value[:-1].strip()
    except ParseException as err:
        print(err)
        return {}
    return books


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.tex'.format(sys.argv[0]))
        sys.exit()

    file = sys.argv[1]
    text = get_text(file)
    books = ply_parse(text)
    for k in books:
        print(k)
        for j in books[k]:
            print('\t{}: {}'.format(j, books[k][j]))


if __name__ == '__main__':
    main()