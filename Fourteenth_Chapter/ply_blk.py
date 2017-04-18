#!/usr/bin/python3

import sys
import ply.lex
import Block


EmptyBlock = 0


class LexError(Exception): pass


def get_file_handle(filename):
    try:
        return open(filename)
    except (EnvironmentError, IOError) as file_err:
        print('Error opening {}: {}'.format(filename, file_err))
        sys.exit()


def parse_blk(fh):
    tokens = ("NODE_START", "NODE_END", "COLOR", "NAME", "NEW_ROWS",
              "EMPTY_NODE")

    t_NODE_START = r"\["
    t_NODE_END = r"\]"
    t_COLOR = r"(?:\#[\dA-Fa-f]{6}|[a-zA-Z]\w*):"
    t_NAME = r"[^][/\n]+"
    t_NEW_ROWS = r"/+"
    t_EMPTY_NODE = r"\[\]"

    t_ignore = ' \t'

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        raise LexError("syntax error: {0}".format(line))


    stack = [Block.create_root_block()]
    block = None
    brackets = 0
    lexer = ply.lex.lex()
    try:
        lexer.input(fh.read())
        for token in lexer:
            if token.type == "NODE_START":
                brackets += 1
                block = Block.create_empty_block()
                stack[-1].children.append(block)
                stack.append(block)
            elif token.type == "NODE_END":
                brackets -= 1
                if brackets < 0:
                    raise LexError("too many ']'s")
                block = None
                stack.pop()
            elif token.type == "COLOR":
                if block is None or Block.is_empty(block):
                    raise LexError("syntax error")
                block.color = token.value[:-1]
            elif token.type == "NAME":
                if block is None or Block.is_empty(block):
                    raise LexError("syntax error")
                block.name = token.value
            elif token.type == "EMPTY_NODE":
                stack[-1].children.append(Block.create_empty_block())
            elif token.type == "NEW_ROWS":
                for x in range(len(token.value)):
                    stack[-1].children.append(Block.create_empty_row())
        if brackets:
            raise LexError("unbalanced brackets []")
    except LexError as err:
        raise ValueError("Error {{0}}:line {0}: {1}".format(
                         token.lineno + 1, err))
    return stack[0]


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.blk'.format(sys.argv[0]))
        sys.exit()

    fh = get_file_handle(sys.argv[1])
    blocks = parse_blk(fh)
    print(blocks)


if __name__ == '__main__':
    main()