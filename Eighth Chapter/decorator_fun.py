#!/usr/bin/python3

import functools


def only_positive(function):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        assert result >= 0, function.__name__ + '() result isn"t >= 0'
        return result
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper


def only_positive2(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        assert result >= 0, function.__name__ + '() result isn"t >= 0'
        return result
    return wrapper


def boundaries(min_val, max_val):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            if result < min_val:
                return min_val
            if result > max_val:
                return max_val
            return result
        return wrapper
    return decorator


@boundaries(0, 100)
def percent(amount, total):
    return (amount / total) * 100


@only_positive
def discriminant(a, b, c):
    return (b ** 2) - (4 * a * c)
