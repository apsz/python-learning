#!/usr/bin/python3
# ~0.7 sec

import os
import argparse
import asyncio
import random


random.seed(1)


def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('word', type=str, help='Word to look for.')
    subparsers = parser.add_subparsers(help='FGrep modes', dest='mode')
    file_parser = subparsers.add_parser('f', help=('Use file mode.\n\t'
                                                   'Usage: f <file1> <file2> <fileN>'))
    file_parser.add_argument('files', type=str, nargs='+')
    directory_parser = subparsers.add_parser('d', help=('Use directory mode.\n\t'
                                                        'Usage: d [-r] <dir1> <dir2> <dirN>\n\t'
                                                        'Optional: -r '
                                                        '(recursively search given directories).'))
    directory_parser.add_argument('-r', '--recursive', action='store_true')
    directory_parser.add_argument('directories', type=str, nargs='+')
    args = parser.parse_args()
    return args


async def read_file(file):
    try:
        with open(file) as fh:
            return fh.readlines()
    except (EnvironmentError, IOError, UnicodeDecodeError, UnicodeEncodeError):
        return


async def print_lines(file, lines):
    for lino, line in lines:
        print('{} {}: {:.80}'.format(file, lino, line))


async def produce_file(queue, args):
    if args.mode == 'f':
        for file in args.files:
            await queue.put(file)
    else:
        for dir in args.directories:
            if args.recursive:
                for root, _, files in os.walk(dir):
                    for file in files:
                        file = os.path.join(root, file)
                        await queue.put(file)
            else:
                for file in os.listdir(dir):
                    if os.path.isfile(file):
                        await queue.put(file)
    await queue.put(None)


async def find_lines(text, word):
    lines = []
    for lino, line in enumerate(text, 1):
        line = line.strip()
        if word in line:
            lines.append((lino, line))
    return lines


async def process_file(queue, loop, word):
    while True:
        file = await queue.get()
        if file is None:
            break

        text = await read_file(file)
        if text:
            found_lines = await find_lines(text, word)
            if found_lines:
               await print_lines(file, found_lines)


def main():
    args = get_args()
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)
    producer = produce_file(queue, args)
    consumer = process_file(queue, loop, args.word)
    loop.run_until_complete(asyncio.gather(producer, consumer))
    loop.close()


if __name__ == '__main__':
    main()


