#!/usr/bin/python3

# 100% score
def solution(l):
    if len(l) == 1:
        return l[0]
    l = sorted(l)
    for i in range(len(l)-1)[::2]:
        if l[i] != l[i+1]:
            return l[i]
    return l[-1]

# def solution(A):
#     return int([i for i in A if A.count(i) == 1][0])