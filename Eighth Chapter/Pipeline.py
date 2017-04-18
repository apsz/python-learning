#!/usr/bin/python3

import functools

def coroutine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return wrapper


@coroutine
def acquire(receiver):
    while True:
        number = (yield)
        if number:
            receiver.send(number)


@coroutine
def to_int(receiver):
    while True:
        number = (yield)
        if number:
            receiver.send(int(number))


@coroutine
def check(receiver, min_val, max_val):
    while True:
        number = (yield)
        if number:
            if (not min_val or number > min_val) and \
               (not max_val or number < max_val):
                receiver.send(number)


@coroutine
def output():
    while True:
        number = (yield)
        if number:
            print(number)


pipeline = acquire(to_int(check(output(), 0, 10)))

for i in range(5, 20):
    pipeline.send(i)

