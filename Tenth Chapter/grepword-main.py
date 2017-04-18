#!/usr/bin/python3

import os
import sys
import optparse
import subprocess


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' word file/path [file1/path1]...')
    parser.add_option('-w', '--word', dest='word', type=str,
                      help=('Specify a single word you will be looking for.'))
    parser.add_option('-r', '--recursive', dest='recurse', action='store_true',
                      default=False, help=('Recurse into subdirectories [default: False]'))
    parser.add_option('-c', '--count', dest='count', type=int, default=1,
                      help=('Number of child processes you want to run [default: 1] [max: 20]'))
    parser.add_option('-d', '--debug', dest='debug_mode', action='store_true',
                      default=False, help=('Debug mode [default: False]'))
    opts, args = parser.parse_args()
    if not args or not opts.word or not (opts.count and 0 < opts.count <= 20):
        parser.print_help()
        sys.exit()
    return opts, opts.word, args


def get_files(paths_or_files, recursive):
    found_files = []
    for path_or_file in paths_or_files:
        if os.path.isfile(path_or_file):
            found_files.append(os.path.abspath(path_or_file))
        else:
            if recursive:
                for root, dirs, files in os.walk(path_or_file):
                    for file in files:
                        found_files.append(os.path.join(root, file))
    return found_files


def main():
    opts, word, args = get_opts_args()
    file_list = get_files(args, opts.recurse)
    files_per_process = len(file_list) // opts.count
    start, end = 0, files_per_process + (len(file_list) % opts.count)
    process_id = 1

    pipes = []
    child_name = os.path.join(os.path.dirname(__file__), 'grepword-child.py')
    while start < len(file_list):
        command = [sys.executable, child_name]
        if opts.debug_mode:
            command.append(str(process_id))
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
        pipes.append(pipe)
        pipe.stdin.write(word.encode(encoding='utf8', errors='ignore') + b'\n')
        for filename in file_list[start:end]:
            pipe.stdin.write(filename.encode('utf8', 'ignore') + b'\n')
        pipe.stdin.close()
        process_id += 1
        start, end = end, end + files_per_process

    while pipes:
        pipe = pipes.pop()
        pipe.wait()


main()
