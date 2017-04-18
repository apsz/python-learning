#!/usr/bin/python3

import sys
from xml.sax.saxutils import escape


def main():
    count = 0
    maxwidth = 100

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
            print_line(file, color, maxwidth)
            count += 1
        except EOFError:
            break

    print_end()


def print_start():
    print("<table border='1'>")


def print_line(line, color, maxwidth):
    print("<tr bgcolor='{0}'>".format(color))
    fields = extract_fields(line)
    for field in fields:
        if not field:
            print("<td></td>")
        else:
            number = field.replace(',', '')
            try:
                number = float(number)
                print("<td align='right'>{0:d}</td>".format(round(number)))
            except ValueError:
                field = field.title()
                field = field.replace(" And ", " and ")
                if len(field) <= maxwidth:
                    field = escape(field)
                else:
                    field = "{0}...".format(escape(field[:maxwidth]))
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