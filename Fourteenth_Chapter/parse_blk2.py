#!/usr/bin/python3


import sys


class ParseError(Exception): pass


class Block:

    def __init__(self, title, color='white'):
        self.title = title
        self.color = color
        self.children = []

    def has_children(self):
        return bool(self.children)


create_root_block = lambda: Block(None, None)
create_empty_block = lambda: Block('')
create_empty_row = lambda: None
is_empty = lambda x: x is None


class Data:

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.brackets = 0
        self.column = 1
        self.row = 1
        self.stack = [create_root_block()]

    def position(self):
        return 'row {}, column {}'.format(self.row, self.column)

    def move_by(self, amount):
        for i in range(amount):
            self._move_by_one()

    def move_to_pos(self, pos):
        while self.pos < pos:
            self. _move_by_one()

    def move_to_char(self, characters):
        while (self.pos < len(self.text) and
               self.text[self.pos].isspace() and
               self.text[self.pos] not in characters):
            self._move_by_one()
        if not self.pos < len(self.text):
            return False
        if self.text[self.pos] in characters:
            return True
        raise ParseError('expected {}: got {}'.format(characters,
                                                    self.text[self.pos]))

    def _move_by_one(self):
        self.pos += 1
        if (self.pos < len(self.text) and
            self.text[self.pos] == '\n'):
            self.column = 1
            self.row += 1
        else:
            self.column += 1


def get_text(file):
    try:
        with open(file) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error processing file {}: {}'.format(file, file_err))
        sys.exit()


def parse_new_row(data):
    data.stack[-1].children.append(create_empty_row())
    data.move_by(1)


def parse_block_data(data, end_pos):
    color = None
    colon = data.text.find(':', data.pos)
    if -1 < colon < end_pos:
        color = data.text[data.pos:colon]
        data.move_to_pos(colon+1)
    name = data.text[data.pos:end_pos].strip()
    data.move_to_pos(end_pos)
    if not name and color is None:
        block = create_empty_block()
    else:
        block = Block(name, color)
    data.stack[-1].children.append(block)
    return block


def parse_block(data):
    data.move_by(1)
    end_block_index = data.text.find(']', data.pos)
    next_block_index = data.text.find('[', data.pos)
    if (next_block_index == -1) or end_block_index < next_block_index:
        parse_block_data(data, end_block_index)
    else:
        block = parse_block_data(data, next_block_index)
        data.stack.append(block)
        parse(data)
        data.stack.pop()


def parse(data):
    while data.pos < len(data.text):
        if not data.move_to_char('[]/'):
            break
        if data.text[data.pos] == '[':
            data.brackets += 1
            parse_block(data)
        elif data.text[data.pos] == ']':
            data.brackets -= 1
            data.move_by(1)
        elif data.text[data.pos] == '/':
            parse_new_row(data)
        else:
            raise ParseError('expected "/ [ or ], '
                             'but got {}'.format(data.text[data.pos]))


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
            sys.argv[1] in ('-h', '--help'):
        print('Usage: {} <filename>.blk')
        sys.exit()

    text = get_text(sys.argv[1])
    data = Data(text)
    try:
        parse(data)
    except ParseError as parse_err:
        raise ValueError('Error {{0}}:{0}: {1}'.format(data.position(),
                                                       parse_err))
    return data.stack[0]


if __name__ == '__main__':
    print(main())
