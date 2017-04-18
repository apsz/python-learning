#!/usr/bin/python3

import random

def main():
    rows = get_int('rows: ', 1, None)
    columns = get_int('columns: ', 1, None)
    minimum = get_int('minimum (or Enter for 0): ', -10000, 0)
    default = 1000
    if default < minimum:
        default = minimum * 2
    maximum = get_int('maximum (or Enter for ' + str(default) + '): ', minimum, default)

    row = 0
    while row < rows:
        column = 0
        line = ''
        while column < columns:
            value = str(random.randint(minimum, maximum))
            while len(value) < 10:
                value = " " + value
            line += value
            column += 1
        print(line)
        row += 1


def get_int(msg, minimum, default):
    while True:
        try:
            user_input = input(msg)
            if not user_input and default is not None:
                return default
            user_input = int(user_input)
            if user_input < minimum:
                print('Must be above minimum.')
                continue
            return user_input
        except ValueError as verr:
            print(verr, 'is not a valid integer.')


main()

