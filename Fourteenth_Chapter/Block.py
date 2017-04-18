#!/usr/bin/python3


class Block:

    def __init__(self, name, color='white'):
        self.name = name
        self.color = color
        self.children = []

    def has_children(self):
        return bool(self.children)


create_root_block = lambda: Block(None, None)
create_empty_block = lambda: Block('')
create_empty_row = lambda: None
is_empty = lambda x: x is None