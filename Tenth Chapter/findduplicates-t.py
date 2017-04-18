#!/usr/bin/python3


import os
import sys
import optparse
import collections
import hashlib
import queue
import threading


class Worker(threading.Thread):

    Md5_lock = threading.Lock()

    def __init__(self, work_queue, result_queue, md5_from_filename,
                 process_id):
        super().__init__()
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.md5_from_filename = md5_from_filename
        self.process_id = process_id

    def run(self):
        while True:
            try:
                size, names = self.work_queue.get()
                self.process(size, names)
            finally:
                self.work_queue.task_done()

    def process(self, size, names):
        md5s = collections.defaultdict(set)
        for filename in names:
            with Worker.Md5_lock:
                md5 = self.md5_from_filename.get(filename, None)
            if md5:
                md5s[md5].add(filename)
            else:
                try:
                    md5 = hashlib.md5()
                    with open(filename, 'rb') as fh:
                        md5.update(fh.read())
                    md5 = md5.digest()
                    md5s[md5].add(filename)
                    with Worker.Md5_lock:
                        self.md5_from_filename[filename] = md5
                except EnvironmentError:
                    continue
        for filenames in md5s.values():
            if len(filenames) == 1:
                continue
            self.result_queue.put('{}Duplicate files ({:n} bytes):'
                                  '\n\t{}'.format(self.process_id, size,
                                  '\n\t'.join(sorted(filenames))))


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' [path]')
    parser.add_option('-c', '--count', dest='count', type=int, default=1,
                      help=('Number of child processes to run [default: 1] [max: 20].'))
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
                      default=False, help=('Launch in debug mode [default: False].'))
    opts, args = parser.parse_args()
    if opts.count and not(0 < opts.count <= 20):
        parser.print_help()
        sys.exit()
    return opts, args[0] if args else '.'


def print_results(result_queue):
    while True:
        try:
            result = result_queue.get()
            if result:
                print(result)
        finally:
            result_queue.task_done()


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
        process_id = '{}: '.format(i + 1) if opts.debug else ''
        worker = Worker(work_queue, result_queue, md5_from_filename,
                        process_id)
        worker.daemon = True
        worker.start()

    results_thread = threading.Thread(target=lambda: print_results(result_queue))
    results_thread.daemon = True
    results_thread.start()

    for size, filename in sorted(data):
        names = data[size, filename]
        if len(names) > 1:
            work_queue.put((size, names))
    work_queue.join()
    result_queue.join()


main()
