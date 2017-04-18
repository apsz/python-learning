#!/usr/bin/python3

import os
import sys
import optparse
import queue
import threading
from xml.etree import ElementTree
from xml.parsers import expat

XML_INIT = '<?xml'

def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') +
                     ' [file1/path1] [file2/path2]')
    parser.add_option('-t', '--threads', dest='count', type=int,
                      default=7, help=('Number of threads to '
                                       'run [default: 7, max: 20].'))
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
                      default=False, help='Debug mode [default: off].')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      default=False, help='Verbose mode [default: off]')
    opts, args = parser.parse_args()
    if not (0 < opts.count <= 20):
        parser.print_help()
        sys.exit()
    return opts, args if args else ('.',)


def print_result(result_queue):
    while True:
        try:
            result = result_queue.get()
            if result:
                print(result, end='')
        finally:
            result_queue.task_done()


class Worker(threading.Thread):

    def __init__(self, thread_id, work_queue,
                 result_queue, debug, verbose):
        super().__init__()
        self.thread_id = thread_id
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.debug = debug
        self.verbose = verbose

    def run(self):
        while True:
            try:
                fullname = self.work_queue.get()
                self.process(fullname)
            finally:
                self.work_queue.task_done()

    def process(self, fullname):
        try:
            with open(fullname, 'rb') as fh:
                init_txt = fh.read(len(XML_INIT))
                if init_txt.decode('utf8', 'ignore') != XML_INIT:
                    if self.verbose:
                        print('{}{}: not a valid xml file.'.format(
                              self.thread_id, fullname))
                    return
            tree = ElementTree.parse(fullname)
            if tree:
                tags = set()
                for node in tree.iter():
                    tags.add(node.tag)
                message = '{}{} has the following tags:\n\t{}\n'.format(
                          self.thread_id, fullname, '\n\t'.join(tags))
                self.result_queue.put(message)
        except (EnvironmentError, IOError) as file_err:
            if self.debug or self.verbose:
                print('{}{} file error: {}'.format(self.thread_id, fullname,
                                                   file_err))
        except (expat.ExpatError, ElementTree.ParseError) as xml_err:
            if self.debug or self.verbose:
                print('{}{} xml error: {}'.format(self.thread_id, fullname,
                                                  xml_err))


def main():
    opts, paths_files = get_opts_args()

    work_queue = queue.Queue()
    result_queue = queue.Queue()
    for i in range(opts.count):
        thread_id = '{}: '.format(i + 1) if opts.debug else ''
        if opts.verbose:
            print('Initializing thread {}...'.format(thread_id[:-2]))
        worker = Worker(thread_id, work_queue, result_queue,
                        opts.debug, opts.verbose)
        worker.daemon = True
        worker.start()
        if opts.verbose:
            print('Thread worker {} ready.'.format(thread_id[:-2]))
    result_thread = threading.Thread(target=lambda:
                                     print_result(result_queue))
    result_thread.daemon = True
    result_thread.start()

    for path_or_file in paths_files:
        if os.path.isfile(path_or_file):
            work_queue.put(os.path.abspath(path_or_file))
        else:
            for root, dirs, files in os.walk(path_or_file):
                for file in files:
                    work_queue.put(os.path.join(root, file))
    work_queue.join()
    result_queue.join()


main()