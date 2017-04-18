#!/usr/bin/python3

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
#
# except ImportError:
#     def do_profile(follow=[]):
#         "Helpful if you accidentally leave in production!"
#         def inner(func):
#             def nothing(*args, **kwargs):
#                 return func(*args, **kwargs)
#             return nothing
#         return inner

# 100% score
def solution(N, A):
    last_high = 0
    arr = [0] * N
    max = 0
    for count, i in enumerate(A[::-1], 1):
        if i > N:
            last_high = -(count)
            break
    if not last_high:
        for i in range(len(A)):
            arr[A[i]-1] += 1
            if arr[A[i]-1] > max:
                max = arr[A[i]-1]
        return arr
    base = 0
    for i in range(len(A) + last_high+1):
        if A[i] > N:
            base = max
        else:
            if base and arr[A[i] - 1] < base:
                arr[A[i] - 1] = base
            arr[A[i]-1] += 1
            if arr[A[i]-1] > max:
                max = arr[A[i]-1]
    arr = [max] * N
    for i in range((len(A) + last_high)+1, len(A)):
        arr[A[i] - 1] += 1
        if arr[A[i] - 1] > max:
            max = arr[A[i] - 1]
    return arr

# @do_profile(follow=[solution])
# def testing():
#     for i in range(100):
#         solution(5, [1, 1, 2, 1, 10, 2, 4, 3, 10, 1, 10, 2, 2, 2, 10, 3, 1, 11])
#
# testing()

print(solution(5, [1, 1, 2, 1, 10, 2, 4, 3, 10, 1, 10, 2, 2, 2, 10, 3, 1, 11]))

# correctness 100% performance 60%
# def solution(N, A):
#     max = 0
#     arr = [0] * N
#     for i in range(len(A)):
#         if A[i] > N:
#             arr = [max] * N
#         else:
#             arr[A[i]-1] += 1
#             if  arr[A[i]-1] > max:
#                 max = arr[A[i]-1]
#     return arr
