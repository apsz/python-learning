#!/usr/bin/python3

import locale
import time
import os
import sys
import optparse
import collections

locale.setlocale(locale.LC_ALL, '')
File = collections.namedtuple('File', 'name modified size')


def main():
    fl_count = 0
    dir_count = 0
    data = collections.defaultdict(list)
    path = ['.']
    opts, args = get_opts_args()

    path = args if args else path
    for arg in path:
        if opts.recursive:
            print_data(*get_recursive(data, opts, arg, fl_count, dir_count))
        else:
            print_data(*get_current_dir(data, opts, arg, fl_count, dir_count))


def get_recursive(data, options, path, fl_count, dir_count):
    for root, dirs, files in os.walk(path):
        for fl in files:
            if not options.hidden and fl.startswith('.'):
                    continue
            fullname = os.path.join(root, fl)
            modified = os.path.getmtime(fullname)
            file = File(fullname, time.strftime('%Y.%m.%d %H:%M:%S', time.gmtime(modified)),
                                                os.path.getsize(fullname))
            data[path].append(file)
            fl_count += 1
        dir_count += len(dirs)
    return data, options, fl_count, dir_count


def get_current_dir(data, options, path, fl_count, dir_count):
    for obj in os.listdir(path):
        if not options.hidden and obj.startswith('.'):
            continue
        fullname = os.path.join(path, obj)
        size = os.path.getsize(fullname)
        if os.path.isfile(fullname):
            fl_count += 1
        else:
            dir_count += 1
            size = '<DIR>'
        modified = os.path.getmtime(fullname)
        file = File(obj, time.strftime('%Y.%m.%d %H:%M:%S',
                                       time.gmtime(modified)), size)
        data[path].append(file)
    return data, options, fl_count, dir_count


def print_data(data, options, fl_count, dir_count):
    sorter = 0
    if options.order[0] == 's':
        sorter = 2
    elif options.order[0] == 'm':
        sorter = 1

    for folder in data.keys():
        for file in sorted(data[folder], key=lambda x: x[sorter] if (isinstance(x[sorter], int)
                                         or isinstance(x[sorter], time.struct_time)) else -1):
            if options.size and options.modified:
                print('{modified} {size:>12{0}} {name}'.format('n' if isinstance(file.size, int)
                                                               else '',**file._asdict()))
            elif not options.size and not options.modified:
                print('{name}'.format(**file._asdict()))
            else:
                if options.size:
                    print('{size:>12{0}} {name}'.format('n' if isinstance(file.size, int)
                                                        else '', **file._asdict()))
                else:
                    print('{modified} {name}'.format(**file._asdict()))
    print('\n{} file{} and {} folder{}'.format(fl_count, '' if fl_count == 1 else 's',
                                               dir_count, '.' if dir_count == 1 else 's.'))


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage('Usage: {} [options] [path1 [path2 [... pathN]]]\n'
                     'The paths are optional; if not given . is used.'.format(sys.argv[0]))
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


