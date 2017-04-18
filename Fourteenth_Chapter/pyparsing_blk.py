#!/usr/bin/python3


import sys
from pyparsing import (Word, Suppress, Forward, CharsNotIn, Group, ZeroOrMore,
                       OneOrMore, Optional, hexnums, alphanums, alphas,
                       ParseException, ParseSyntaxException)
import Block


EmptyBlock = 0


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error processing file {}: {}'.format(file, file_err))
        sys.exit()


def populate_children(items, stack):
    for item in items:
        if isinstance(item, Block.Block):
            stack[-1].children.append(item)
        elif isinstance(item, list) and item:
            stack.append(stack[-1].children[-1])
            populate_children(item, stack)
            stack.pop()
        elif isinstance(item, int):
            if item == EmptyBlock:
                stack[-1].children.append(Block.create_empty_block())
            else:
                for i in range(item):
                    stack[-1].children.append(Block.create_empty_row())


def pyparse_blk(text):

    def add_new_block(tokens):
        return Block.Block(tokens.title, tokens.color if
                           tokens.color else 'white')

    left_bracket, right_bracket = map(Suppress, '[]')
    empty_block = (left_bracket + right_bracket)('empty_block').setParseAction(
        lambda tokens: EmptyBlock)
    new_lines = Word('/')('new_lines').setParseAction(
        lambda tokens: len(tokens.new_lines))
    title = CharsNotIn('[]/\n')('title').setParseAction(
        lambda tokens: tokens.title.strip())
    color = (Word('#', hexnums, exact=7) | Word(alphanums, alphas))('color')
    blocks = Forward()
    block_data = Optional(color + Suppress(':')) + Optional(title)
    block_data.addParseAction(add_new_block)
    block = left_bracket - block_data + blocks + right_bracket
    blocks << Group(ZeroOrMore(Optional(new_lines) +
                               OneOrMore(empty_block | block)))

    stack = [Block.create_root_block()]
    try:
        results = blocks.parseString(text, parseAll=True)
        assert len(results) == 1
        items = results.asList()[0]
        populate_children(items, stack)
    except (ParseException, ParseSyntaxException) as parse_err:
        raise ValueError('Error {{0}}: syntax error, line {0}'.format(
            parse_err.lineno))
    return stack[0]


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 \
            or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.blk'.format(sys.argv[0]))
        sys.exit()

    text = get_text(sys.argv[1])
    parsed_blocks = pyparse_blk(text)
    return parsed_blocks


if __name__ == '__main__':
    print(main())

