#!/usr/bin/python3

import time
import random


# import re
# def solution(N):
#     str_N = str(bin(N))
#     print(str_N)
#     if re.search('[1]0*[1]', str_N):
#         return max([len(x) for x in str_N.split('1')
#                     if all([k == '0' for k in x])])
#     return 0

# import re
# def solution(N):
#     str_N = str(bin(N))
#     matches = re.findall(r'(?=(1[0]+1))', str_N)
#     return len(min(matches))-2 if matches else 0
#     # results = [len(str(match.group(1))) for match in matches]
#     # return max(results)-2 if results else 0
#
# print(solution(15))
# print(solution(328))
# # print(solution(1965))
# print(solution(2))
# print(solution(66561))
#
# set.pop()

# def solution(A):
#     for i in A:
#         if A.count(i) == 1:
#             return i
#
# def solution(A):
#     return int([i for i in A if A.count(i) == 1][0])

# def solution(A):
#     uniqe = find_uniqe(A[::2]) + find_uniqe(A[1::2])
#     return uniqe[0] or None
#
# def find_uniqe(l):
#     value = 0
#     while len(l) >= 2:
#         value = l[0]
#         if l[1] == value:
#             del l[1]
#         else:
#             del l[0]
#     if l[0] == value:
#         del l[0]
#     return l

#     A = sorted(A)
#     print(A)
#     for i in set(A):
#         if find_all(A, i) == 1:
#             return i
#
#
# def find_all(A, val):
#     count = 0
#     index = binary_search(A, val)
#     while index < len(A) and A[index] == val:
#         count += 1
#         del A[index]
#     return count
#
#
# def binary_search(A, val):
#     left, right = 0, len(A)
#     while left < right:
#         middle = (left + right) // 2
#         if A[middle] < val:
#             left = middle + 1
#         else:
#             right = middle
#     return left

# Perfect score solution
def solution(l):
    if len(l) == 1:
        return l[0]
    l = sorted(l)
    for i in range(len(l)-1)[::2]:
        if l[i] != l[i+1]:
            return l[i]
    return l[-1]

#print(solution([9, 3, 9, 3, 9, 7, 9]))
    # if len(l) == 1:
    #     return l[0]
    # l = sorted(l)
    # for i in range(len(l)-2):
    #     if l[i-1] != l[i] != l[i+1]:
    #         return l[i]
    #     if i + 2 == len(l)-1:
    #         return l[-1]

    # l = sorted(l)
    # for i in set(l):
    #     index = binary_search(l, i)
    #     if (index == len(l)-1):
    #         return i
    #     if l[index+1] != i:
    #         return i

def binary_search(A, val):
    left, right = 0, len(A)
    while left < right:
        middle = (left + right) // 2
        if A[middle] < val:
            left = middle + 1
        else:
            right = middle
    return left


    # evens = l[::2]
    # odds = l[1::2]
    # work_list = evens if not len(evens) % 2 == 0 else odds
    # for i in set(work_list):
    #     print(work_list)
    #     work_list.remove(i)
    #     if i not in work_list:
    #         return i
a = list(range(1000000)) + list(range(1000000)) + [1000002]
start_time = time.time()
print(solution(a))
print(solution([42]))
print(solution([9, 3, 9, 3, 9, 7, 9]))
print("--- {} seconds ---".format(time.time() - start_time))
