#!/usr/bin/python3

import locale
import time
import os
import optparse

locale.setlocale(locale.LC_ALL, '')


def main():
    paths = ['.']
    files = []
    directories = []
    opts, args = get_opts_args()
    if args:
        paths = args
    for path in paths:
        if opts.recursive:
            for root, dirs, fls in os.walk(path):
                dirs[:] = [dir for dir in dirs if not dir.startswith('.')]
                for file in fls:
                    if not opts.hidden and file.startswith('.'):
                        continue
                    fullname = os.path.join(root, file)
                    files.append(fullname)
            process_files(files, [], opts)
        else:
            for obj in os.listdir(path):
                if not opts.hidden and obj.startswith('.'):
                    continue
                fullname = os.path.join(path, obj)
                if os.path.isfile(fullname):
                    files.append(fullname.split(os.path.sep)[-1])
                else:
                    directories.append(fullname)
            process_files(files, directories, opts)


def process_files(files, dirs, opts):
    data = {}
    dir_len = 0

    for file in files:
        line = ''
        name = file
        size = os.path.getsize(file)
        modified = time.strftime('%Y.%m.%d %H:%M:%S', time.gmtime(os.path.getmtime(file)))
        s_key = name
        if opts.order[0] == 'm':
            s_key = modified
        elif opts.order[0] == 's':
            s_key = size
        if opts.modified:
            line += '{modified:<19}'.format(**locals())
        if opts.size:
            line += '{size:>14n}'.format(**locals())
        dir_len = len(line) + 1
        line += '{}{:>}'.format(' ' if line else '', name
                                if not name.startswith('.' + os.path.sep) else name[2:])
        data[(s_key, name, modified, size)] = line
    for key in sorted(data.keys()):
        print(data[key])
    for dir in dirs:
        print('{0}{1}'.format(' '*dir_len, dir.split(os.path.sep)[1] + os.path.sep))
    print('{} file{} and {} director{}'.format(len(files), 's' if len(files) != 1 else '',
                                               len(dirs), 'ies.' if len(dirs) !=1 else 'y.'))


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage('Usage: %prog [options] [path1 [path2 [... pathN]]]\n'
                     'The paths are optional; if not given . is used.')
    parser.add_option('-H', '--hidden', dest='hidden', default=False,
                      action='store_true', help=('show hidden files [default: off]'))
    parser.add_option('-m', '--modified', dest='modified', default=False,
                      action='store_true', help=('show last modified date/time [default: off]'))
    parser.add_option('-o', '--order', dest='order', default='name',
                      choices=['name', 'n', 'modified', 'm', 'size', 's'],
                      help=("order by ('name', 'n', 'modified', 'm', 'size', 's') [default: name]"))
    parser.add_option('-r', '--recursive', dest='recursive', default=False,
                      action='store_true', help=('recurse into subdirectories [default: off]'))
    parser.add_option('-s', '--size', dest='size', default=False,
                      action='store_true', help=('show sizes [default: off]'))
    return parser.parse_args()


main()