#!/usr/bin/python3


import sys
import subprocess


class RangeError(Exception): pass
class RowRangeError(RangeError): pass
class ColumnRangeError(RangeError): pass


_CHAR_ASSERT_TEMPLATE = ("char must be a single character: '{0}' "
                         "is too long")
_max_rows = 25
_max_columns = 80
_grid = []
_background_char = " "


if sys.platform.endswith('win'):
    def clear_screen():
        subprocess.call(['cmd.exe', '/C', 'cls'])
else:
    def clear_screen():
        subprocess.call(['clear'])


def resize(max_rows, max_columns, char=None):
    assert max_rows > 0 and max_columns > 0, "Too small"
    global _max_columns, _max_rows, _grid, _background_char
    if char:
        _background_char = char
    _max_rows = max_rows
    _max_columns = max_columns
    _grid = [[_background_char for column in range(_max_columns)]
                               for row in range(_max_rows)]


def add_horizontal_line(row, column0, column1, char='-'):
    try:
        for column in range(column0, column1):
            _grid[row][column] = char
    except IndexError:
        if not 0 <= row <= _max_rows:
            raise RowRangeError()
        raise ColumnRangeError()


def add_vertical_line(column, row0, row1, char='|'):
    try:
        for row in range(row0, row1):
            _grid[row][column] = char
    except IndexError:
        if not 0 <= column <= _max_columns:
            raise ColumnRangeError()
        raise RowRangeError()


def add_rectangle(row0, col0, row1, col1, char="*", fill=False):
    try:
        for row in range(row0, row1):
            for column in range(col0, col1):
                if fill:
                    _grid[row][column] = char
                    continue
                if row == row0 or row == row1-1 or column == col0 or column == col1-1:
                    _grid[row][column] = char
    except IndexError:
        pass


def add_text(row, column, text, border_char=None):
    try:
        if border_char:
            text = '{0}\n{1}{2}{1}\n{0}'.format(border_char*(len(text)+2), border_char, text)
            text = text.split('\n')
            for i in range(len(text)):
                rw = row + i
                for j in range(len(text[i])):
                    cl = column + j
                    _grid[rw][cl] = text[i][j]
        else:
            for i in range(len(text)):
                cl = column + i
                _grid[row][cl] = text[i]
    except IndexError:
        if not 0 <= column <= _max_columns:
            raise ColumnRangeError()
        raise RowRangeError()


def render(clear=True):
    # if clear:
    #     clear_screen()
    for row in range(_max_rows):
        print(''.join([(_grid[row][column]) for column in range(_max_columns)]))


def get_size():
    return _max_rows, _max_columns


def char_at(row, column):
    return _grid[row][column]


resize(14, 50)
add_rectangle(0, 0, *get_size())
add_vertical_line(5, 10, 13)
add_vertical_line(2, 9, 12, "!")
add_horizontal_line(3, 10, 20, "+")
add_rectangle(0, 0, 5, 5, "%")
add_rectangle(5, 7, 12, 40, "#", True)
add_rectangle(7, 9, 10, 38, " ")
add_text(8, 10, "This is the CharGrid module")
add_text(1, 32, "Pleasantville", "@")
add_rectangle(6, 42, 11, 46, fill=True)
render()