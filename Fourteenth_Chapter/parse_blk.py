#!/usr/bin/python3


import sys


class LexError(Exception): pass


class Block:

    def __init__(self, name, color='white'):
        self.name = name
        self.color = color
        self.children = []

    def has_children(self):
        return bool(self.children)


get_root_block = lambda: Block(None, None)
get_empty_block = lambda: Block('')
get_new_row = lambda: None
is_empty = lambda x: x is None


class Data:

    def __init__(self, text):
        self.pos = 0
        self.column = 1
        self.line = 1
        self.brackets = 0
        self.text = text
        self.stack = [get_root_block()]

    def location(self):
        return 'line {}, column {}'.format(self.line, self.column)

    def _advance_by_one(self):
        self.pos += 1
        if (self.pos < len(self.text) and
            self.text[self.pos] == '\n'):
            self.column = 1
            self.line += 1
        else:
            self.column += 1

    def advance_by(self, amount):
        for x in range(amount):
            self._advance_by_one()

    def advance_to_position(self, end_pos):
        while self.pos < end_pos:
            self._advance_by_one()

    def advance_up_to(self, characters):
        while (self.pos < len(self.text) and
               self.text[self.pos].isspace() and
               self.text[self.pos] not in characters):
            self._advance_by_one()
        if not self.pos < len(self.text):
            return False
        if self.text[self.pos] in characters:
            return True
        raise LexError('expected {}: got {}'.format(characters,
                                                    self.text[self.pos]))


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error while processing {}: {}'.format(file, file_err))
        sys.exit()


def parse_new_row(data):
    data.stack[-1].children.append(get_new_row())
    data.advance_by(1)


def parse_block_data(data, end_pos):
    color = None
    colon = data.text.find(':', data.pos)
    if -1 < colon < end_pos:
        color = data.text[data.pos:colon]
        data.advance_to_position(colon+1)
    name = data.text[data.pos:end_pos].strip()
    data.advance_to_position(end_pos)
    if not name and color is None:
        block = get_empty_block()
    else:
        block = Block(name, color)
    data.stack[-1].children.append(block)
    return block


def parse_block(data):
    data.advance_by(1)
    end_block = data.text.find(']', data.pos)
    new_block = data.text.find('[', data.pos)
    if new_block == -1 or (end_block < new_block):
        parse_block_data(data, end_block)
    else:
        block = parse_block_data(data, new_block)
        data.stack.append(block)
        parse(data)
        data.stack.pop()


def parse(data):
    while data.pos < len(data.text):
        if not data.advance_up_to('[]/'):
            break
        if data.text[data.pos] == '[':
            data.brackets += 1
            parse_block(data)
        elif data.text[data.pos] == ']':
            data.brackets -= 1
            data.advance_by(1)
        elif data.text[data.pos] == '/':
            parse_new_row(data)
        else:
            raise LexError('expecting "/ [ or ], '
                           'but got {}'.format(data.text[data.pos]))
    if data.brackets:
        raise LexError('ran out of text expecting '
                       '{}.'.format('[' if not data.brackets else ']'))


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} file.blk')
        sys.exit()

    text = get_text(sys.argv[1])
    data = Data(text)
    try:
        parse(data)
    except LexError as parsing_err:
        raise ValueError('Error {{0}}:{0}: {1}'.format(data.location(),
                                                       parsing_err))
    return data.stack[0]


if __name__ == '__main__':
    print(main())