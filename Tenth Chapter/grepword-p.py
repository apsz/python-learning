#!/usr/bin/python3

import os
import sys
import optparse
import subprocess


def parse_options():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' [word]')
    parser.add_option('-w', '--word', dest='word', type='str',
                      help=('Provide a single word you"re searching for.'))
    parser.add_option('-r', '--recursive', dest='recurse', action='store_true', default=False,
                      help=('Recurse into subdirectories [default: False].'))
    parser.add_option('-c', '--count', dest='count', type='int', default=1,
                      help=('Number of child processes you want to run [default: 1] [max: 20].'))
    parser.add_option('-d', '--debug', dest='debug', action='store_true', default=False,
                      help=('Run the program in debug mode [default: False]'))
    opts, args = parser.parse_args()
    if not args or not opts.word or (opts.count and not(0 < opts.count <= 20)):
        parser.print_help()
        sys.exit()
    return opts, opts.word, args


def get_files(paths_or_files, recursive):
    files_list = []
    for path_or_file in paths_or_files:
        if os.path.isfile(path_or_file):
            files_list.append(os.path.abspath(path_or_file))
        else:
            if recursive:
                for root, dirs, files in os.walk(path_or_file):
                    for file in files:
                        files_list.append(os.path.join(root, file))
    return files_list


def main():
    child = os.path.join(os.path.dirname(__file__),
                         'grepword-p-child.py')
    opts, word, args = parse_options()
    file_list = get_files(args, opts.recurse)
    files_per_process = len(file_list) // opts.count
    start, end = (0, files_per_process + (len(file_list) % opts.count))
    number = 1

    pipes = []
    while start < len(file_list):
        command = [sys.executable, child]
        print(command)
        if opts.debug:
            command.append(str(number))
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
        pipes.append(pipe)
        pipe.stdin.write(word.encode('utf8') + b'\n')
        for filename in file_list[start:end]:
            pipe.stdin.write(filename.encode('utf8') + b'\n')
        pipe.stdin.close()
        number += 1
        start, end = end, end + files_per_process

    while pipes:
        pipe = pipes.pop()
        pipe.wait()


main()


