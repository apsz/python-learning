#!/usr/bin/python3

import os
import sys
import functools


def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        generator = func(*args, **kwargs)
        next(generator)
        return generator
    return wrapper


@coroutine
def reporter():
    while True:
        path = (yield)
        print(path)


@coroutine
def get_files(receiver):
    while True:
        path = (yield)
        if os.path.isfile(path):
            receiver.send(os.path.abspath(path))
        else:
            for root, dirs, files in os.walk(path):
                for file in files:
                    receiver.send(os.path.abspath(
                        os.path.join(root, file)))

@coroutine
def suffix_matcher(receiver, suffixes):
    while True:
        path = (yield)
        for suffix in suffixes:
            if path.endswith(suffix):
                receiver.send(path)


@coroutine
def size_matcher(receiver, min_size=None, max_size=None):
    while True:
        path = (yield)
        size = os.path.getsize(path)
        if (not min_size or size >= min_size) and \
           (not max_size or size <= max_size):
            receiver.send(path)


pipeline = size_matcher(reporter(), min_size=1024*2)
pipeline = suffix_matcher(pipeline, ('.py',))
pipeline = get_files(pipeline)


for file in sys.argv[1:]:
    pipeline.send(file)