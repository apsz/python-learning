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


def get_files(files_paths, recursive):
    file_list = []
    for file_or_path in files_paths:
        if os.path.isfile(file_or_path):
            file_list.append(os.path.abspath(file_or_path))
        else:
            if recursive:
                for root, dirs, files in os.walk(file_or_path):
                    for file in files:
                        file_list.append(os.path.join(root, file))
    return file_list


def main():
    child = os.path.join(os.path.dirname(__file__), 'grepword_child.py')
    opts, word, files_paths = parse_options()
    file_list = get_files(files_paths, opts.recurse)
    files_per_process = len(file_list) // opts.count
    start, end = (0, (files_per_process + len(file_list) % opts.count))
    process_id = 1

    pipes = []
    found_files = []
    while start < len(file_list):
        command = [sys.executable, child]
        if opts.debug:
            command.append(str(process_id))
        pipe = subprocess.Popen(command, stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
        pipes.append((pipe, pipe.stdout))
        pipe.stdin.write(word.encode('utf8') + b'\n')
        for file in file_list[start:end]:
            pipe.stdin.write(file.encode('utf8') + b'\n')
        pipe.stdin.close()
        #found_files.append(pipe.communicate()[0].decode('utf8', 'ignore').rstrip())
        #pipe.stdout.close()
        start, end = end, end + files_per_process
        process_id += 1

    while pipes:
        pipe, out = pipes.pop()
        found_files.extend(out.readlines())
        pipe.wait()

    for line in sorted(found_files):
        print(line.decode("utf8").rstrip())
    #print('\n'.join(found_files))


main()