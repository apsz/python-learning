#!/usr/bin/python3


import datetime
import xml.sax.saxutils


class CancelledErr(Exception): pass


COPYRIGHT_TEMPLATE = "Copyright (c) {0} {1}. All rights reserved."
STYLESHEET_TEMPLATE = ('<link rel="stylesheet" type="text/css" '
                        'media="all" href="{0}" />\n')
HTML_TEMPLATE = """<?xml version="1.0"?>
                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" \
                    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                    <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
                    <head>
                    <title>{title}</title>
                    <!-- {copyr} -->
                    <meta name="Description" content="{description}" />
                    <meta name="Keywords" content="{keywords}" />
                    <meta equiv="content-type" content="text/html; charset=utf-8" />
                    {stylesheet}\
                    </head>
                    <body>
                    </body>
                    </html>"""


def main():
    data = dict(name=None, year=datetime.date.today().year, filename=None,
                title=None, description=None, keywords=None, stylesheet=None)

    while True:
        print("\nMake HTML Skeleton\n")
        try:
            get_data(data)
            save_skeleton(**data)
        except CancelledErr:
            print('Cancelled')
        if (get_string("\nCreate another (y/n)?", default="y").lower() not in {"y", "yes"}):
            break


def get_data(data):
    name = get_string('Enter your name (for copyright): ', data['name'])
    input_validation(name)
    year = get_int('Enter copyright year [{year}]: '.format(**data), data['year'])
    input_validation(year)
    filename = get_string('Enter filename: ')
    input_validation(filename)
    if not filename.endswith(('.html', '.htm')):
        filename +=  '.html'
    title = get_string('Enter title: ')
    input_validation(title)
    description, keywords = get_description()
    stylesheet = get_string('Enter the stylesheet filename (optional): ')
    data.update(name=name, year=year, filename=filename, title=title,
                description=description, keywords=keywords, stylesheet=stylesheet)


def get_string(msg, default=None):
    value = input(msg)
    if not value and default:
        value = default
    return value


def get_int(msg, default=None):
    value = None
    while True:
        try:
            value = int(input(msg))
            return value
        except (ValueError, TypeError):
            if not value and default:
                value = default
                return value
            print('Not a valid year')


def get_description(k=None):
    k = []
    description = get_string('Enter description (optional): ')
    if description:
        while True:
            keyword = input('Enter a keyword (optional): ')
            if not keyword:
                break
            k.append(keyword)
    return description, k


def input_validation(value):
    if not value:
        raise CancelledErr


def save_skeleton(year, name, title, description, keywords,
                  stylesheet, filename):
    copyr = COPYRIGHT_TEMPLATE.format(year, xml.sax.saxutils.escape(name))
    title = xml.sax.saxutils.escape(title)
    description = xml.sax.saxutils.escape(description)
    keywords = ",".join([xml.sax.saxutils.escape(k)
                        for k in keywords]) if keywords else ""
    stylesheet = (STYLESHEET_TEMPLATE.format(stylesheet)
                  if stylesheet else "")
    html = HTML_TEMPLATE.format(**locals())

    fh = None
    try:
        fh = open(filename, "w", encoding="utf8")
        fh.write(html)
    except EnvironmentError as err:
        print("ERROR", err)
    else:
        print("Saved skeleton", filename)
    finally:
        if fh is not None:
            fh.close()


main()