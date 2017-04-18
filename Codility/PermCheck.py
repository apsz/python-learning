#!/usr/bin/python3

# 100% score
def solution(A):
    l = sorted(A)
    if len(l) == 1:
        return 1 if l[0] == 1 else 0
    for i in range(len(A)-1):
        if l[i+1] - l[i] != 1 or i+1 != l[i]:
            return 0
    return 1


print(solution([1, 3, 4, 2]))