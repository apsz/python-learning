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

# l_for_v = {'A': 1, 'C': 2, 'G': 3, 'T': 4}
# get_l = lambda x: l_for_v[x]
#
# def solution(S, P, Q):
#     result = []
#     for i, j in zip(P, Q):
#         result.append(sorted(map(get_l, set(S[i:j+1])))[0])
#     return result


l_for_v = {'A': 1, 'C': 2, 'G': 3, 'T': 4}

def solution(S, P, Q):
    result = []
    for i, j in zip(P, Q):
        mn = 'Z'
        out = False
        for k in S[i:j+1]:
            if k == 'A':
                result.append(l_for_v[k])
                out = True
                break
            if k < mn:
                mn = k
        if not out:
            result.append(l_for_v[mn])
    return result
#import random
# l_for_v = {'A': 1, 'C': 2, 'G': 3, 'T': 4}
#
# def solution(S, P, Q):
#     result = []
#     for i in range(len(P)):
#         diff = P[i] - Q[i]
#         if not diff:
#             result.append(l_for_v[S[P[i]]])
#             continue
#         if abs(diff) == 1:
#             if S[P[i]] < S[Q[i]]:
#                 result.append(l_for_v[S[P[i]]])
#             else:
#                 result.append(l_for_v[S[Q[i]]])
#         else:
#             mx = 'Z'
#             out = False
#             for j in S[P[i]:Q[i]+1]:
#                 if j == 'A':
#                     result.append(1)
#                     out = True
#                     break
#                 if j < mx:
#                     mx = j
#             if not out:
#                 result.append(l_for_v[mx])
#     return result
#import random
# l_for_v = {'A': 1, 'C': 2, 'G': 3, 'T': 4}
# def solution(S, P, Q):
#     slcs = ((S[P[i]:Q[i]+1]) for i in range(len(P)))
#     return list(l_for_v[min(slc)] for slc in slcs)

# @do_profile(follow=[solution])
def testing():
    for i in range(1000):
        solution('CAGCCTA', [2, 5, 0], [4, 5, 6])

testing()

#print(solution('CAGCCTA', [2, 5, 0], [4, 5, 6]))
# a = '{}'.format('CAGCCTA'*1000000)
# print(a)
# l1 = [random.randint(0, r) for r in range(900)]
# l2 = [random.randint(0, x) for x in range(900)]
# print(l1)
# print(l2)
# print(solution(a, l1, l2))