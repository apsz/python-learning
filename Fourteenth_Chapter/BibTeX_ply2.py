#!/usr/bin/python3


import sys
import re
import ply.lex


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

    tokens = ('START', 'BOOK_ID', 'KEY', 'TEXT_VALUE',
              'NUM_VALUE', 'END', 'COMMA')

    WHITESPACE = re.compile('\s+')
    t_ignore = ' \t\n'
    t_ignore_START = r'@Book'
    t_ignore_COMMA = r','
    t_ignore_END = r'\}'

    t_KEY = r'[a-zA-Z]\w*'

    def t_BOOK_ID(t):
        r'\{[^\s,]*'
        t.value = t.value[1:]
        return t

    def t_TEXT_VALUE(t):
        r'=\s*"[^="]+"'
        t.value = WHITESPACE.sub(' ', t.value[1:].lstrip()[1:-1].strip())
        return t

    def t_NUM_VALUE(t):
        r'=\s*\d+'
        t.value = int(t.value[1:].lstrip())
        return t

    def t_newline(t):
        r'\n+'
        t.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        print('failed to parse line {0}: {1}'.format(t.lineno + 1,
                                                     line))

    books = {}
    book = key = None
    lexer = ply.lex.lex()
    lexer.input(text.replace('\n', ' '))
    for token in lexer:
        if token.type == 'BOOK_ID':
            books[token.value] = book = {}
            continue
        if book is None:
            print('missing start of book line {0}'.format(token.lineno))
        elif token.type == 'KEY':
            key = token.value
            continue
        if key is None:
            print('missing key line {0}'.format(token.lineno))
        elif token.type in ('TEXT_VALUE', 'NUM_VALUE'):
            book[key] = token.value
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