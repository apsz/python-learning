#!/usr/bin/python3

# 100% score
def solution(X, A):
    a_ss = set(range(1, X+1))
    for i in range(1, len(A)+1):
        if A[i-1] in a_ss:
            a_ss.discard(A[i-1])
        if len(a_ss) == 0:
            return i-1
    return -1


print(solution(5, [1, 2, 3, 5, 1, 4, 3, 9]))