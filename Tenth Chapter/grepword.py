#!/usr/bin/python3

import os
import sys
import optparse


def get_opts_args():
    parser = optparse.OptionParser()
    parser.add_option('-w', '--word', dest='word', type=str, default='',
                      help=('Type in a single word you want to search for.'))
    opts, args = parser.parse_args()
    if not args or not opts.word:
        parser.print_help()
        sys.exit()
    return opts, args


def main():
    opts, args = get_opts_args()
    for file_or_dir in args:
        if os.path.isfile(file_or_dir):
            try:
                with open(file_or_dir) as fh:
                    for lino, line in enumerate(fh):
                        if opts.word in line:
                            print('file: {}, line no.: {}\t{}'.format(
                                  file_or_dir, lino, line), end='')
            except (IOError, EnvironmentError, UnicodeDecodeError) as f_err:
                print('Error {}.\nSkipping {}'.format(f_err, file_or_dir))
        else:
            for root, dirs, files in os.walk(file_or_dir):
                for file in files:
                    try:
                        with open(os.path.join(root, file)) as fh:
                            for lino, line in enumerate(fh):
                                if opts.word in line:
                                    print('file: {}, line no.: {}\t{}'.format(
                                        file, lino, line), end='')
                    except (IOError, EnvironmentError, UnicodeDecodeError) as f_err:
                        print('Error {}.\nSkipping {}'.format(f_err, file))


main()


