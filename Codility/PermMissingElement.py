#!/usr/bin/python3

# 100% score
def solution(A):
    if not A:
        return 1
    l = sorted(A)
    count = 0
    for i in range(1, l[-1]):
        if l[count] != i:
            return i
        count += 1
    return l[-1]+1

print(solution([1, 2, 4]))


