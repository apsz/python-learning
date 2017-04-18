#!/usr/bin/python3

# 100% score
def solution(A, B, K):
    nA = None
    nB = B / K

    if A % K == 0:
        nA = A / K
    else:
        nA = A / K + 1

    if nA > nB:
        return 0
    else:
        return round(nB - nA + 1)

print(solution(6, 11, 3))