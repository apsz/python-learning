#!/usr/bin/python3

import sys
import math
import cmath


def main():
    print("ax\N{SUPERSCRIPT TWO} + bx + c = 0")
    a = get_float('a: ', False)
    b = get_float('b: ', True)
    c = get_float('c: ', True)

    x1 = None
    x2 = None
    discriminant = (b ** 2) + (4 * a * c)
    if not discriminant:
        x1 = -(b / (2 * a))
    else:
        if discriminant > 0:
            root = math.sqrt(discriminant)
        else:
            root = cmath.sqrt(discriminant)
        x1 = (-b + root) / (2 * a)
        x2 = (-b - root) / (2 * a)

    equation = "{}x\N{SUPERSCRIPT TWO}".format(a)
    if b:
        if b > 0:
            equation += " + {}x".format(b)
        else:
            equation += " - {}x".format(abs(b))
    if c:
        if c > 0:
            equation += " + {}".format(c)
        else:
            equation += " - {}".format(abs(c))

    equation += " = 0 \N{RIGHTWARDS ARROW} x = {0}".format(x1)
    equation = (equation).format(**locals())
    if x2 is not None:
        equation += " or x = {0}".format(x2)
    print(equation)


def get_float(msg, allow_zero):
    x = None
    while x is None:
        try:
            x = float(input(msg))
            if not allow_zero and abs(x) < sys.float_info.epsilon:
                print('zero is not allowed')
                x = None
        except ValueError as verr:
            print(verr)
    return x


main()