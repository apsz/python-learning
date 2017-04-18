#!/usr/bin/python3

import string
import sys
import collections


def main():
    words = collections.defaultdict(int)
    strip = string.whitespace + string.punctuation + string.digits + "\"'"
    for filename in sys.argv[1:]:
        for line in open(filename):
            for word in line.lower().split():
                word = word.strip(strip)
                if len(word) > 2:
                    words[word] += 1
    for k, v in sorted(words.items(), key=occurence_sort):
        print("'{0}' occurs {1} times".format(k, v))


def occurence_sort(words):
    return words[1], words[0]