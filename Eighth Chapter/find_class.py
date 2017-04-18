#!/usr/bin/python3

import os
import sys
import datetime
import time
import optparse
import functools

def validated(meth):
    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        result = meth(*args, **kwargs)
        print(meth.__name__)
        return result
    return wrapper

def opts_to_properties(opts_names):
    def decorator(cls):
        nonlocal opts_names
        for name in opts_names:
            setattr(cls, name, eval('@validated\n'
                                    'lambda self: {}.{}'.format(
                                    cls.__name__, name)))
        return cls
    return decorator


class RecalculateBytes:

    def __init__(self, attr_name, unit_type):
        self.__attr_name = attr_name
        self.__unit_type = 1024 if unit_type == 'k' else 1024**2


    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.__attr_name)*self.__unit_type


@opts_to_properties(('bigger', 'smaller', 'days', 'output', 'suffixes'))
class Find:

    bigger_mb = RecalculateBytes('bigger', 'm')
    bigger_kb = RecalculateBytes('bigger', 'k')
    smaller_mb = RecalculateBytes('smaller', 'm')
    smaller_kb = RecalculateBytes('smaller', 'k')

    def __init__(self, opts, paths):
        self.__opts = opts
        self.__paths = paths
        self.__matched_files = []


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
    if not args:
        parser.print_help()
        sys.exit()
    return opts, args


def main():
    find = Find(*get_opts_args())
    print(find._Find__paths)
    print(find._Find__opts)
    print(find.output)
    print(dir(find))

main()