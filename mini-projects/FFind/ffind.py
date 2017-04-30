#!/usr/bin/python3


import os
import argparse
import datetime
import time
import asyncio
import random

random.seed(1)


def get_bytes(byte_size):
    if byte_size[-1] in 'KkMm':
        multiplier = 1024 if byte_size[-1] in 'Kk' else 1024**2
        return int(byte_size[:-1]) * multiplier
    return int(byte_size)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--days', type=int,
                      help=('Only files younger than <days> will be shown.'))
    parser.add_argument('-b', '--bigger', type=str,
                      help=('Discard all files bigger than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes.'))
    parser.add_argument('-s', '--smaller', type=str,
                      help=('Discard all files smaller than the given size. '
                            'Add "m" for megabytes or "k" for kilobytes.'))
    parser.add_argument('-o', '--output', type=str, nargs='+',
                        choices=['size', 'date'],
                        help=('Specifies what should be output (size date). '
                              'Filenames are always printed.'))
    parser.add_argument('-u', '--suffix', type=str, nargs='+',
                      help=('Show only files with the given suffix(es). Multiple '
                            'suffixes are allowed.'))
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='Path to recursively search for files.')
    args = parser.parse_args()
    if args.bigger:
        args.bigger = get_bytes(args.bigger)
    if args.smaller:
        args.smaller = get_bytes(args.smaller)
    if (args.smaller and args.bigger) and (args.bigger < args.smaller):
        parser.error('bigger < smaller')
    if args.days:
        days = datetime.datetime.now() - datetime.timedelta(days=args.days)
        args.days = time.mktime(days.timetuple())
    return args


async def produce_files(queue, path):
    for root, dirs, files in os.walk(args.path):
        for file in files:
            await queue.put((root, file))
    await queue.put(None)


async def get_file_and_stats(root, file):
    return (os.path.abspath(file), os.stat(os.path.join(root, file)))


async def match_file_size(file, smaller=None, bigger=None):
    if smaller is None and bigger is None:
        return file
    if smaller and file[1].st_size < smaller:
        return file
    elif bigger and file[1].st_size > bigger:
        return file


async def match_file_date(file, date=None):
    if date is None:
        return file
    if file[1].st_mtime > date:
        return file


async def match_file_suffix(file, suffixes):
    if not suffixes:
        return file
    for suffix in suffixes:
        if file[0].endswith(suffix):
            return file


async def main(args, queue):
    while True:
        filetuple_or_none = await queue.get()
        if filetuple_or_none is None:
            break

        file_and_stats = await get_file_and_stats(*filetuple_or_none)
        file_matched_size = await match_file_size(file_and_stats, args.smaller, args.bigger)
        file_matched_date = await match_file_date(file_and_stats, args.days)
        file_matched_suffix = await match_file_suffix(file_and_stats, args.suffix)

        if file_matched_size and file_matched_date and file_matched_suffix:
            txt = '{:<30.30}'.format(os.path.basename(file_matched_size[0]))
            if args.output:
                if 'date' in args.output:
                    txt += ' {}'.format(datetime.date.fromtimestamp(file_matched_size[1].st_mtime))
                if 'size' in args.output:
                    txt += ' {:<15}'.format(file_matched_size[1].st_size)
            print(txt)


if __name__ == '__main__':
    args = get_args()

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)
    producer = produce_files(queue, args.path)
    consumer = main(args, queue)
    loop.run_until_complete(asyncio.gather(producer, consumer))
    loop.close()