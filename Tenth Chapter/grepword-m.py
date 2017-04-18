#!/usr/bin/python3

import os
import sys
import optparse
import multiprocessing


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage(parser.get_usage().strip('\n') + ' word file1/path1 [file2/path2]...')
    parser.add_option('-w', '--word', dest='word', type=str,
                      help=('Single word you will be looking for.'))
    parser.add_option('-c', '--count', dest='count', type=int, default=1,
                      help=('Number of child processes to run [default: 1] [max: 20].'))
    parser.add_option('-r', '--recursive', dest='recurse', action='store_true',
                      default=False, help=('Recurse into subdirectories [default: False].'))
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
                      default=False, help=('Launch in debug mode [default: False].'))
    opts, args = parser.parse_args()
    if not args or not opts.word or (opts.count and not (0 < opts.count <= 20)):
        parser.print_help()
        sys.exit()
    return opts, opts.word, args


def get_files(files_or_paths, recursive):
    files_list = []
    for file_or_path in files_or_paths:
        if os.path.isfile(file_or_path):
            files_list.append(os.path.abspath(file_or_path))
        else:
            if recursive:
                for root, dirs, files in os.walk(file_or_path):
                    for file in files:
                        files_list.append(os.path.join(root, file))
    return files_list


class Worker(multiprocessing.Process):

    def __init__(self, work_queue, word, process_id):
        super().__init__()
        self.work_queue = work_queue
        self.word = word
        self.process_id = process_id

    def run(self):
        while True:
            try:
                file = self.work_queue.get()
                self.process(file)
            finally:
                self.work_queue.task_done()

    def process(self, file):
        BLOCK_SIZE = 8000
        previous = ''

        try:
            with open(file, 'rb') as fh:
                while True:
                    block = fh.read(BLOCK_SIZE)
                    if not block:
                        break
                    block_decoded = block.decode('utf8', 'ignore')
                    if (self.word in block_decoded or
                        self.word in previous[-len(self.word):] +
                        block_decoded[:len(self.word)]):
                        print('{}{}'.format(self.process_id, file))
                        break
                    if len(block_decoded) != BLOCK_SIZE:
                        break
                    previous = block_decoded
        except EnvironmentError as env_err:
            print('{}{}{}'.format(self.process_id, file, env_err))


def main():
    opts, word, args = get_opts_args()
    file_list = get_files(args, opts.recurse)

    work_queue = multiprocessing.JoinableQueue()
    for i in range(opts.count):
        process_id = '{}: '.format(i + 1) if opts.debug else ''
        worker = Worker(work_queue, word, process_id)
        worker.daemon = True
        worker.start()
        for file in file_list:
            work_queue.put(file)
    work_queue.join()


if __name__ == "__main__":
    main()