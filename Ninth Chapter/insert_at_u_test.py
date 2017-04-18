#!/usr/bin/python3

import cProfile

# try:
#     from line_profiler import LineProfiler
#
#     def do_profile(follow=[]):
#         def inner(func):
#             def profiled_func(*args, **kwargs):
#                 try:
#                     profiler = LineProfiler()
#                     profiler.add_function(func)
#                     for f in follow:
#                         profiler.add_function(f)
#                     profiler.enable_by_count()
#                     return func(*args, **kwargs)
#                 finally:
#                     profiler.print_stats()
#             return profiled_func
#         return inner
# except ImportError:
#     def do_profile(follow=[]):
#         "Helpful if you accidentally leave in production!"
#         def inner(func):
#             def nothing(*args, **kwargs):
#                 return func(*args, **kwargs)
#             return nothing
#         return inner


def insert_at(string, position, insert):
    """Returns a copy of string with insert inserted at the position
    >>> string = "ABCDE"
    >>> result = []
    >>> for i in range(-2, len(string) + 2):
    ...     result.append(insert_at(string, i, "-"))
    >>> result[:5]
    ['ABC-DE', 'ABCD-E', '-ABCDE', 'A-BCDE', 'AB-CDE']
    >>> result[5:]
    ['ABC-DE', 'ABCD-E', 'ABCDE-', 'ABCDE-']
    """
    return string[:position] + insert + string[position:]

def test():
    for i in range(10000):
        insert_at('whatever', 0, str(i))


#test()
# if __name__ == '__main__':
#     cProfile.run('test()')

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
