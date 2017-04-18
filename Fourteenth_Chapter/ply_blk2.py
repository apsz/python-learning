#!/usr/bin/python3


import sys
import ply.lex
import Block


class ParseError(Exception): pass


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Cannot open/read file: {}'.format(file_err))
        sys.exit()


def ply_parse(text):

    tokens = ('BEGIN', 'END', 'COLOR', 'TITLE', 'EMPTY_BLK', 'NEW_LINES')

    t_BEGIN = r'\['
    t_END = r'\]'
    t_COLOR = r'(?:\#[\da-fA-F]{6}|[a-zA-Z]\w*):'
    t_TITLE = r'[^][/\n]+'
    t_EMPTY_BLK = r'\[\]'
    t_NEW_LINES = r'/+'

    t_ignore = ' \t'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        new_line_idx = line.find('\n')
        line = line if new_line_idx == -1 else line[:new_line_idx]
        raise ParseError('cannot parse line {}'.format(line))

    lexer = ply.lex.lex()
    stack = [Block.create_root_block()]
    block = None
    brackets = 0
    try:
        lexer.input(text)
        for token in lexer:
            if token.type == 'BEGIN':
                block = Block.create_empty_block()
                stack[-1].children.append(block)
                stack.append(block)
                brackets += 1
            elif token.type == 'END':
                block = None
                stack.pop()
                brackets -= 1
                if brackets < 0:
                    raise ParseError('too many "]"')
            elif token.type == 'COLOR':
                if block is None or Block.is_empty(block):
                    raise ParseError("syntax error")
                block.color = token.value[:-1]
            elif token.type == 'TITLE':
                if block is None or Block.is_empty(block):
                    raise ParseError("syntax error")
                block.title = token.value
            elif token.type == 'NEW_LINES':
                for x in range(len(token.value)):
                    stack[-1].children.append(Block.create_empty_row())
            elif token.type == 'EMPTY_BLK':
                stack[-1].children.append(Block.create_empty_block)
        if brackets:
            raise ParseError('unbalanced brackets')
    except ParseError as err:
        raise ValueError('Error {{0}}: line {0}: {1}'.format(token.lineno + 1, err))
    return stack[0]


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.blk'.format(sys.argv[0]))
        sys.exit()

    file = sys.argv[1]
    text = get_text(file)

    try:
        block_tree = ply_parse(text)
        return block_tree
    except ParseError as parse_err:
        print('Error: {}'.format(parse_err))


if __name__ == '__main__':
    main()