#!/usr/bin/python3


import sys
from pyparsing import (Suppress, Word, CharsNotIn, Group, Optional,
                       Forward, ZeroOrMore, OneOrMore,
                       alphas, alphanums, hexnums,
                       ParseException, ParseSyntaxException)
import Block


EmptyBlock = 0


def get_text(filename):
    try:
        with open(filename) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error processing {}: {}'.format(filename, file_err))
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

    def create_add_block(tokens):
        return Block.Block(tokens.title, tokens.color if tokens.color else 'white')

    left_bracket, right_bracket, equal_sign = map(Suppress, '[]=')
    color = (Word('#', hexnums, exact=7) | Word(alphanums, alphas))('color')
    empty_block = (left_bracket + right_bracket)('empty_block').setParseAction(
        lambda: EmptyBlock)
    new_lines = Word('/')('new_lines').setParseAction(
        lambda tokens: len(tokens.new_lines))
    title = CharsNotIn('[]/\n')('title').setParseAction(
        lambda tokens: tokens.title.strip())
    block_data = Optional(color + Suppress(':')) + Optional(title)
    block_data.addParseAction(create_add_block)
    blocks = Forward()
    block = left_bracket + block_data + blocks + right_bracket
    blocks << Group(ZeroOrMore(Optional(new_lines) + OneOrMore(empty_block | block)))

    stack = [Block.create_root_block()]
    try:
        result = blocks.parseString(text, parseAll=True)
        assert len(result) == 1
        blocks_list = result.asList()[0]
        populate_children(blocks_list, stack)
    except (ParseSyntaxException, ParseException) as parse_err:
        raise ValueError('Error {{0}}: {0}'.format(parse_err.lineno))
    return stack[0]


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.blk'.format(sys.argv[0]))
        sys.exit()

    text_to_parse = get_text(sys.argv[1])
    blocks_tree = pyparse_blk(text_to_parse)
    return blocks_tree


if __name__ == '__main__':
    main()

