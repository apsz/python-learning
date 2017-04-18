#!/usr/bin/python3


import sys
import ply.lex


def get_file_handle(filename):
    try:
        return open(filename)
    except (EnvironmentError, IOError) as file_err:
        print('Error opening {}: {}'.format(filename, file_err))
        sys.exit()


def parse_pls_ply(fh, lowercase_keys=False):

    tokens = ['INI_HEADER', 'KEY', 'VALUE', 'COMMENT']

    t_ignore_INI_HEADER = r'\[[^]]+\]'
    t_ignore_COMMENT = r'\#.*'

    def t_KEY(t):
        r'\w+'
        if lowercase_keys:
            t.value = t.value.lower()
        return t

    def t_VALUE(t):
        r'=.*'
        t.value = t.value[1:].strip()
        return t

    def t_newline(t):
        r'\n'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        new_line_index = line.find('\n')
        line = line if new_line_index == -1 else line[:new_line_index]
        print('Failed to parse line {}: {}'.format(t.lineno + 1, line))

    keys_values = {}
    lexer = ply.lex.lex()
    lexer.input(fh.read())
    key = None
    for token in lexer:
        if token.type == 'KEY':
            key = token.value
        elif token.type == 'VALUE':
            if key is not None:
                keys_values[key] = token.value
                key = None
            else:
                print('Parsing error: no key found '
                      'for value: {}'.format(token.value))
    return keys_values


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.pls'.format(sys.argv[0]))
        sys.exit()

    fh = get_file_handle(sys.argv[1])
    keys_values = parse_pls_ply(fh, True)
    for k in keys_values:
        print('{}: {}'.format(k, keys_values[k]))


if __name__ == '__main__':
    main()