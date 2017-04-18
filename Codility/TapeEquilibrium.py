#!/usr/bin/python3

# 100% score
import heapq
def solution(A):
    h = []
    val_a = 0
    val_b = 0
    for i in range(len(A)):
        if i == 0:
            continue
        if i == 1:
            val_a = sum(A[:i])
            val_b = sum(A[i:])
            diff = abs(val_a - val_b)
            heapq.heappush(h, diff)
            continue
        val_a = val_a + A[i-1]
        val_b = val_b - A[i-1]
        diff = abs(val_a - val_b)
        heapq.heappush(h, diff)
    return h[0]


print(solution([-1000, 1000]))
