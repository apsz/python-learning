#!/usr/bin/python3

import os
import sys
import optparse
import functools
import datetime
import time
import timeit


class OptError(Exception): pass


def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        decorated = function(*args, **kwargs)
        next(decorated)
        return decorated
    return wrapper


@coroutine
def get_files(receiver):
    while True:
        file_or_path = (yield)
        if os.path.isfile(file_or_path):
            receiver.send((os.path.abspath(file_or_path),
                           os.stat(file_or_path)))
        else:
            for root, dirs, files in os.walk(file_or_path):
                for file in files:
                    receiver.send((os.path.abspath(file),
                                   os.stat(os.path.join(root, file))))


@coroutine
def size_matcher(receiver, smaller=None, bigger=None):
    while True:
        file = (yield)
        if smaller and file[1].st_size < smaller:
            receiver.send(file)
        elif bigger and file[1].st_size > bigger:
            receiver.send(file)


@coroutine
def date_matcher(receiver, border_date):
    while True:
        file = (yield)
        if file[1].st_mtime > border_date:
            receiver.send(file)


@coroutine
def suffix_matcher(receiver, suffixes):
    while True:
        file = (yield)
        if file[0].endswith(suffixes):
            receiver.send(file)


@coroutine
def print_matched(size=False, date=False):
    while True:
        file = (yield)
        txt = '{:<30.30}'.format(os.path.basename(file[0]))
        if date:
            txt += ' {}'.format(datetime.date.fromtimestamp(file[1].st_mtime))
        if size:
            txt += ' {:<15}'.format(file[1].st_size)
        print(txt)


def get_bytes(byte_size):
    if byte_size[-1] in 'KkMm':
        multiplier = 1024 if byte_size[-1] in 'Kk' else 1024**2
        return int(byte_size[:-1]) * multiplier
    return int(byte_size)


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' file1/path1, file2/path2...')
    parser.add_option('-d', '--days', dest='days', type=int,
                      help=('Only files younger than <days> will be shown.'))
    parser.add_option('-b', '--bigger', dest='bigger', type=str,
                      help=('Discard all files bigger than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes.'))
    parser.add_option('-s', '--smaller', dest='smaller', type=str,
                      help=('Discard all files smaller than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes.'))
    parser.add_option('-o', '--output', dest='output', type=str,
                      help=('Specifies what should be output (size, date). '
                            'Filenames are always output.'))
    parser.add_option('-u', '--suffix', dest='suffix', type=str,
                      help=('Show only files with the given suffix(es). Multiple '
                            'suffixes have to be comma-separated.'))
    opts, args = parser.parse_args()

    try:
        if not args:
            raise OptError()
        if opts.bigger:
            opts.bigger = get_bytes(opts.bigger)
        if opts.smaller:
            opts.smaller = get_bytes(opts.smaller)
        if (opts.smaller and opts.bigger) and (opts.bigger < opts.smaller):
            raise OptError()
        if opts.suffix:
            if ',' in opts.suffix:
                opts.suffix = tuple(opts.suffix.split(','))
            else:
                opts.suffix = (opts.suffix,)
        if opts.output:
            if ',' in opts.output:
                opts.output = opts.output.split(',')
                if len(opts.output) == 2 and ('size' not in opts.output or
                                               'date' not in opts.output):
                    raise OptError()
        if opts.days:
            days = datetime.datetime.now() - datetime.timedelta(days=opts.days)
            opts.days = time.mktime(days.timetuple())
        return opts, args
    except OptError:
        parser.print_help()
        sys.exit()


def main():
    opts, args = get_opts_args()

    pipes = []
    pipes.append(print_matched(size=True if (opts.output and 'size' in opts.output) else False,
                               date=True if (opts.output and 'date' in opts.output) else False))
    if opts.smaller:
        pipes.append(size_matcher(pipes[-1], smaller=opts.smaller))
    if opts.bigger:
        pipes.append(size_matcher(pipes[-1], bigger=opts.bigger))
    if opts.suffix:
        pipes.append(suffix_matcher(pipes[-1], opts.suffix))
    if opts.days:
        pipes.append(date_matcher(pipes[-1], opts.days))
    pipes.append(get_files(pipes[-1]))

    try:
        for file_or_dir in args:
            pipes[-1].send(file_or_dir)
    finally:
        for pipe in pipes:
            pipe.close()


main()
# if __name__ == '__main__':
#     function = 'get_bytes'
#     arg = '123123123123312m'
#     t = timeit.Timer('{}("{}")'.format(function, arg),
#                      'from __main__ import {}'.format(function))
#     sec = t.timeit(100000) / 100000
#     print("{function} {sec:.6f} sec".format(**locals()))

