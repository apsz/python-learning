#!/usr/bin/python3

# 100% score
def solution(A):
    count_total = 0
    count_ones = 0
    zeros = False
    ones = False
    for i in reversed(A):
        if not i:
            ones = True
            count_total += count_ones
        else:
            zeros = True
            count_ones += 1
    if not (zeros and ones):
        return 0
    if count_total > 1000000000:
        return -1
    return count_total


print(solution([1, 1, 0, 1, 1, 1]))