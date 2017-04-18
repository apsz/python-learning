#!/usr/bin/python3

import os
import sys
import collections
import optparse
import threading
import queue
import hashlib


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' [path]')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help=('Launch script in debug mode [default: off]'))
    parser.add_option('-t', '--threads', dest='count', type=int, default=7,
                      help=('Number of threads to run [default: 7]'))
    opts, args = parser.parse_args()
    if not 0 < opts.count <= 20:
        parser.print_help()
        sys.exit()
    return opts, args[0] if args else '.'


def print_result(result_queue):
    while True:
        try:
            result = result_queue.get()
            if result:
                print(result)
        finally:
            result_queue.task_done()


class Worker(threading.Thread):

    Md5_Lock = threading.Lock()

    def __init__(self, thread_id, work_queue,
                 result_queue, md5_from_filename):
        super().__init__()
        self.thread_id = thread_id
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.md5_from_filename = md5_from_filename

    def run(self):
        while True:
            try:
                size, fullnames = self.work_queue.get()
                self.process(size, fullnames)
            finally:
                self.work_queue.task_done()


    def process(self, size, fullnames):
        md5s_to_filename = collections.defaultdict(set)
        for fullname in fullnames:
            with Worker.Md5_Lock:
                md5 = self.md5_from_filename.get(fullname, None)
            if md5:
                md5s_to_filename[md5] = fullname
            else:
                try:
                    md5 = hashlib.md5()
                    with open(fullname, 'rb') as fh:
                        md5.update(fh.read())
                    md5 = md5.digest()
                    md5s_to_filename[md5].add(fullname)
                    with Worker.Md5_Lock:
                        self.md5_from_filename[fullname] = md5
                except EnvironmentError:
                    continue

        for filenames in md5s_to_filename.values():
            if len(filenames) == 1:
                continue
            self.result_queue.put('{}Duplicate files ({:n} bytes):'
                                  '\n\t{}'.format(self.thread_id, size,
                                                  '\n\t'.join(sorted(filenames))))


def main():
    opts, path = get_opts_args()
    data = collections.defaultdict(list)
    for root, dirs, files in os.walk(path):
        for file in files:
            fullname = os.path.join(root, file)
            try:
                key = (os.path.getsize(fullname), file)
            except EnvironmentError:
                continue
            if key[0] == 0:
                continue
            data[key].append(fullname)

    work_queue = queue.PriorityQueue()
    result_queue = queue.Queue()
    md5_from_filename = {}
    for i in range(opts.count):
        thread_id = '{}: '.format(i + 1) if opts.debug else ''
        worker = Worker(thread_id, work_queue,
                        result_queue, md5_from_filename)
        worker.daemon = True
        worker.start()
    result_worker = threading.Thread(target=lambda: print_result(result_queue))
    result_worker.daemon = True
    result_worker.start()

    for size, filename in sorted(data.keys()):
        fullnames = data[size, filename]
        if len(filename) > 1:
            work_queue.put((size, fullnames))
    work_queue.join()
    result_queue.join()


main()