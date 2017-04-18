#!/usr/bin/python3


import os
import collections


def main():
    data = collections.defaultdict(list)
    path = 'C:\\Windows\\System32\\'

    for roots, dirs, filenames in os.walk(path):
        try:
            for file in filenames:
                fullname = os.path.join(path, file)
                key = (os.path.getsize(fullname), file)
                data[key].append(fullname)
        except EnvironmentError:
            continue

    for size, filename in sorted(data):
        names = data[(size, filename)]
        if len(names) > 1:
            print("{filename} ({size} bytes) may be duplicated "
                  "({0} files):".format(len(names), **locals()))
            for name in names:
                print("\t{0}".format(name))


main()