#!/usr/bin/python3

import sys
from xml.sax.saxutils import escape


USAGE = """usage:
           {} [maxwidth=int] [format=str] < infile.csv > outfile.html
           maxwidth is an optional integer; if specified, it sets the maximum
           number of characters that can be output for string fields,
           otherwise a default of 100 characters is used.
           format is the format to use for numbers; if not specified it
           defaults to ".0f"."""

def main():
    count = 0

    maxwidth, formt = process_options()

    if maxwidth and formt:
        print_start()

        while True:
            try:
                file = input()
                if not count:
                    color = "lightgreen"
                elif not count % 2:
                    color = "white"
                else:
                    color = "lightyellow"
                print_line(file, color, maxwidth, formt)
                count += 1
            except EOFError:
                break

        print_end()


def process_options():
    maxwidth = 100
    formt = ".0f"

    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print(USAGE.format(sys.argv[0]))
            return None, None
        try:
            for arg in sys.argv[1:]:
                if "maxwidth" in arg:
                    maxwidth = int(arg.split("=")[1])
                elif "format" in arg:
                    formt = str(arg.split("=")[1])
        except ValueError:
            pass
    return maxwidth, formt


def print_start():
    print("<table border='1'>")


def print_line(line, color, maxwidth, formt):
    print("<tr bgcolor='{0}'>".format(color))
    fields = extract_fields(line)
    for field in fields:
        if not field:
            print("<td></td>")
        else:
            number = field.replace(',', '')
            try:
                number = float(number)
                print("<td align='right'>{0:{1}}</td>".format(number, formt))
            except ValueError:
                field = field.title()
                field = field.replace(" And ", " and ")
                if len(field) <= maxwidth:
                    field = escape(field)
                else:
                    field = "{0:}...".format(escape(field[:maxwidth]))
                print("<td>{0}</td>".format(field))
    print("</tr>")


def extract_fields(line):
    fields = []
    field = ''
    quote = None
    for c in line:
        if c in "\"'":
            if quote is None:
                quote = c
            elif quote == c:
                quote = None
            else:
                field += c
            continue
        if quote is None and c == ',':
            fields.append(field)
            field = ''
        else:
            field += c
    if field:
        fields.append(field)
    return fields


def print_end():
    print("</table>")


main()