#!/usr/bin/python3

import os
import collections


def main():
    data = collections.defaultdict(list)
    path = 'C:\\Windows\\System32\\'

    for root, dir, files in os.walk(path):
        try:
            for filename in files:
                fullname = os.path.join(path, filename)
                key = (filename, os.path.getsize(fullname))
                data[key].append(fullname)
        except EnvironmentError as err:
            continue

    for filename, size in sorted(data):
        if len(data[(filename, size)]) > 1:
            print('{filename} size ({size}) might be duplicated: '.format(**locals()))
            for file in data[(filename, size)]:
                print('\t{}'.format(file))

main()


