#!/usr/bin/python3

import os
import sys
import re
import optparse


class OptionError(Exception): pass


def main():
    new_opts, opts, args = get_opts_args()
    print(new_opts, opts, args)


def get_opts_args():
    parser = optparse.OptionParser()
    parser.add_option('-d', '--days', dest='days', type=int,
                      help=('Only files younger than <days> will be shown.'))
    parser.add_option('-b', '--bigger', dest='max_size', type=str,
                      help=('Discard all files bigger than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes'))
    parser.add_option('-s', '--smaller', dest='min_size', type=str,
                      help=('Discard all files smaller than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes'))
    parser.add_option('-o', '--output', dest='output_type', type=str,
                      help=('Specifies what should be output. Filenames are always output'))
    parser.add_option('-u', '--suffix', dest='suffixes', type=str,
                      help=('Show only files with the given suffix(es). If multiple '
                            'suffixes have to be comma-separated.'))
    opts, args = parser.parse_args()
    new_opts = {}
    try:
        for size_arg, name in zip((opts.max_size, opts.min_size),
                                  ('max_size', 'min_size')):
            if size_arg and not re.match(re.compile(r'^\d+[k,m]*$'), opts.max_size):
                raise OptionError()
            if size_arg and size_arg[-1] == 'k':
                new_opts[name] = int(size_arg[:-1])*1024
            elif size_arg and size_arg[-1] == 'm':
                new_opts[name] = int(size_arg[:-1]*1024**2)
            elif size_arg:
                new_opts[name] = int(size_arg)
        if opts.output_type:
            if ',' in opts.output_type:
                date_and_size = opts.output_type.split(',')
                if not ('size' in date_and_size and 'date' in date_and_size) \
                        or len(date_and_size) > 2:
                    raise OptionError()
            else:
                if not opts.output_type == 'size' and not opts.output_type == 'date':
                    raise OptionError()
        if opts.suffixes and ',' in opts.suffixes:
            new_opts['suffixes'] = (suffix for suffix in opts.suffixes.split(','))
        else:
            new_opts['suffixes'] = [opts.suffixes]
        return new_opts, opts, args
    except OptionError:
        parser.print_help()
        sys.exit()


main()