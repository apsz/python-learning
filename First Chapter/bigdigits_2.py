#!/usr/bin/python3

import sys

Zero = ["  ***  ", " *   * ", "*     *", "*     *", "*     *", " *   * ", "  ***  "]
One = [" * ", "** ", " * ", " * ", " * ", " * ", "***"]
Two = [" *** ", "*   *", "*  * ", "  *  ", " *   ", "*    ", "*****"]
Three = [" *** ", "*   *", "    *", "  ** ", "    *", "*   *", " *** "]
Four = ["   *  ", "  **  ", " * *  ", "*  *  ", "******", "   *  ", "   *  "]
Five = ["*****", "*    ", "*    ", " *** ", "    *", "*   *", " *** "]
Six = [" *** ", "*    ", "*    ", "**** ", "*   *", "*   *", " *** "]
Seven = ["*****", "    *", "   * ", "  *  ", " *   ", "*    ", "*    "]
Eight = [" *** ", "*   *", "*   *", " *** ", "*   *", "*   *", " *** "]
Nine = [" ****", "*   *", "*   *", " ****", "    *", "    *", "    *"]

Numbers = (Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine)

def main():
    try:
        for i in range(7):
            line_to_print = ""
            for par in sys.argv[1]:
                line_to_print += Numbers[int(par)][i].replace("*", par) + " "
            print(line_to_print)
    except IndexError:
        print("Usage:", sys.argv[0], "[number/digit]")
    except ValueError as verr:
        print("Not a valid digit", str(verr))

main()

