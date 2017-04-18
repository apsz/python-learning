#!/usr/bin/python3

import os
import sys
import optparse
import threading
import queue
from xml.parsers import expat
from xml.etree import ElementTree


XML_TAG = '<?xml'


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' file1/path1 [file2/path2]...')
    parser.add_option('-t', '--threads', dest='count', type=int,
                      default=7, help=('number of threads to use [default: 7, max: 20].'))
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False, help=('Show more information [default: off].'))
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help=('Launch in debug mode [default: off].'))
    opts, args = parser.parse_args()
    if not (0 < opts.count <= 20):
        parser.print_help()
        sys.exit()
    return opts, args if args else ('.', )


def get_files_recursive(files_or_paths):
    files_list = []
    for file_or_path in files_or_paths:
        try:
            if os.path.isfile(file_or_path):
                files_list.append((os.path.getsize(os.path.abspath(file_or_path)),
                                   os.path.abspath(file_or_path)))
            else:
                for root, dirs, files in os.walk(file_or_path):
                    for file in files:
                        files_list.append((os.path.getsize(os.path.join(root, file)),
                                           os.path.join(root, file)))
        except (EnvironmentError, FileNotFoundError):
            continue
    return files_list


def print_result(result_queue):
    while True:
        try:
            result = result_queue.get()
            if result:
                print(result)
        finally:
            result_queue.task_done()


class Worker(threading.Thread):

    def __init__(self, thread_id, work_queue, result_queue,
                 verbose, debug):
        super().__init__()
        self.thread_id = thread_id
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.verbose = verbose
        self.debug = debug

    def run(self):
        while True:
            try:
                size, fullname = self.work_queue.get()
                self.process(fullname)
            finally:
                self.work_queue.task_done()

    def process(self, fullname):
        try:
            tree = ElementTree.parse(fullname)
            if tree:
                tags = set()
                if self.verbose:
                    print('{}processing {}...'.format(self.thread_id, fullname))
                for node in tree.iter():
                    tags.add(node.tag)
                result = '{}{} {}:\n\t{}'.format(self.thread_id, fullname,
                                                 'has the following tags', '\n\t'.join(tags))
                self.result_queue.put(result)
        except (EnvironmentError, expat.ExpatError) as err:
            print('{}Error while processing {}: {}'.format(self.thread_id,
                                                           fullname, err))


def main():
    opts, paths_files = get_opts_args()
    files_list = get_files_recursive(paths_files)

    work_queue = queue.PriorityQueue()
    result_queue = queue.Queue()
    for i in range(opts.count):
        thread_id = '{}: '.format(i + 1) if opts.debug else ''
        if opts.verbose:
            print('Initializing worker thread {}...'.format(thread_id[:-2]))
        worker = Worker(thread_id, work_queue, result_queue,
                        opts.verbose, opts.debug)
        worker.daemon = True
        worker.start()
        if opts.verbose:
            print('Worker thread {} ready.'.format(thread_id[:-2]))

    result_worker = threading.Thread(target=lambda: print_result(result_queue))
    result_worker.daemon = True
    result_worker.start()
    if opts.verbose:
        print('Result thread initiated and waiting for results.')

    for file in sorted(files_list):
        size, fullname = file
        try:
            with open(fullname, 'rb') as fh:
                if fh.read(len(XML_TAG)).decode('utf8', 'ignore') == XML_TAG:
                    work_queue.put(file)
                else:
                    if opts.verbose:
                        print('Skipping {}: not a valid xml file.'.format(fullname))
        except EnvironmentError as f_err:
            print('Skipping {}: {}'.format(fullname, f_err))
    work_queue.join()
    result_queue.join()


main()
