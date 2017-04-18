#!/usr/bin/python3

import os
import sys
import datetime
import time
import optparse
import cProfile
#import pdb


class OptError(Exception): pass


class Find:

    def __init__(self, opts, paths):
        #pdb.set_trace()
        self.__bigger = opts.bigger
        self.__smaller = opts.smaller
        self.__output = opts.output
        self.__suffixes = opts.suffixes
        self.__days = opts.days
        self.__paths = paths
        self.__matched_files = []

    def __validated(self, filename, file_stats):
        if self.__bigger and self.__bigger > file_stats.st_size:
            return False
        if self.__smaller and self.__smaller < file_stats.st_size:
            return False
        if self.__suffixes and not filename.endswith(self.__suffixes):
            return False
        if self.__days and file_stats.st_mtime < self.__days:
            return False
        return True

    def __get_files(self):
        for path_or_file in self.__paths:
            if os.path.isfile(path_or_file):
                if self.__validated(path_or_file, os.stat(path_or_file)):
                    self.__matched_files.append((path_or_file,
                                                os.stat(path_or_file)))
            else:
                for root, dirs, files in os.walk(path_or_file):
                    for file in files:
                        if self.__validated(file, os.stat(os.path.join(root, file))):
                            self.__matched_files.append((file,
                                                         os.stat(os.path.join(root, file))))

    def print_matched(self):
        self.__get_files()
        for file, stats in self.__matched_files:
            txt = '{:<30.30}'.format(file)
            if self.__output and 'date' in self.__output:
                txt += ' {}'.format(datetime.date.fromtimestamp(stats.st_mtime))
            if self.__output and 'size' in self.__output:
                txt += ' {:<15}'.format(stats.st_size)
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
    parser.add_option('-u', '--suffix', dest='suffixes', type=str,
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
        if opts.suffixes:
            if ',' in opts.suffixes:
                opts.suffixes = tuple(opts.suffixes.split(','))
            else:
                opts.suffixes = (opts.suffixes,)
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
    find = Find(*get_opts_args())
    find.print_matched()


main()
# if __name__ == '__main__':
#     cProfile.run('for i in range(100000): get_bytes("1231237176676321m")')
