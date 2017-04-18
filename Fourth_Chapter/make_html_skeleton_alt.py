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
        try:
            update_data(data)
            make_skeleton(**data)
        except CancelledErr:
            print('Cancelled')
        if get_str('\nCreate another? (y/n)', default='y').lower() not in {'y', 'yes'}:
            break


def save_skeleton(filename, html_template):
    fh = None
    try:
        fh = open(filename, 'w')
        fh.write(html_template)
    except (IOError, EnvironmentError) as file_err:
        print('Error while writing to file: {}'.format(file_err))
    else:
        print('Skeleton saved to file {}'.format(filename))
    finally:
        if fh:
            fh.close()


def make_skeleton(name, year, filename, title, description, keywords, stylesheet):
    copyr = COPYRIGHT_TEMPLATE.format(year, xml.sax.saxutils.escape(name))
    stylesheet = STYLESHEET_TEMPLATE.format(xml.sax.saxutils.escape(stylesheet) if stylesheet else '')
    title = xml.sax.saxutils.escape(title)
    description = xml.sax.saxutils.escape(description) if description else ''
    keywords = ','.join([xml.sax.saxutils.escape(k) for k in keywords]) if keywords else ''
    html = HTML_TEMPLATE.format(**locals())
    save_skeleton(filename, html)


def update_data(data, keywords=None):
    keywords = []
    name = get_str('Enter your name (for copyright)', 'name', data['name'])
    validate_input(name)
    year = get_int('Enter copyright year', 'year', data['year'],
                   2000, datetime.date.today().year +1)
    validate_input(year)
    filename = get_str('Enter filename', 'filename')
    if not filename.endswith(('.html', 'htm')):
        filename += '.html'
    validate_input(filename)
    title = get_str('Enter title', 'title')
    validate_input(title)
    description = get_str('Enter description (optional)', 'description')
    while True:
        keyword = get_str('Enter a keyword (optional)', 'keyword')
        if keyword:
            keywords.append(keyword)
        else:
            break
    stylesheet = get_str('Enter the stylesheet filename (optional)', 'stylesheet')

    data.update(name=name, year=year, filename=filename, title=title,
                description=description, keywords=keywords, stylesheet=stylesheet)


def get_str(msg, name='string', default=None, min_len=0, max_len=80):
    msg += ': ' if not default else '[{}]: '.format(default)
    while True:
        try:
            value = input(msg)
            if not value:
                if default:
                    return default
                if not min_len:
                    return ''
            if not min_len <= len(value) <= max_len:
                raise ValueError('{name} must be at least {min_len} '
                                 'and at most {max_len} length'.format(**locals()))
            return value
        except ValueError as verr:
            print('Error: {}'.format(verr))


def get_int(msg, name='integer', default=None, min_val=0, max_val=100, zero_ok=False):
    msg += ': ' if not default else '[{}]: '.format(default)
    while True:
        try:
            value = input(msg)
            if not value:
                if default:
                    return default
                if int(value) == 0 and zero_ok:
                    return value
            if not min_val <= int(value) <= max_val:
                raise ValueError('{name} must be between {min_val} and {max_val}'.format(**locals()))
            return int(value)
        except (ValueError, TypeError) as conversion_err:
            print('Error: {}'.format(conversion_err))


def validate_input(input):
    if not input:
        raise CancelledErr


main()