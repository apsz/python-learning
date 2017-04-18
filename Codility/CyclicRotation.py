#!/usr/bin/python3

# 100% score
def solution(A, K):
    if not A or len(A) == 1 or K % len(A) == 0:
        return A
    original = A[:]
    arr_len = len(original)
    for i in range(len(original)):
        shift = i + K
        if shift <= arr_len-1:
            A[shift] = original[i]
        else:
            while shift > arr_len-1:
                shift -= arr_len
            A[shift] = original[i]
    return A


print(solution([], 2))
# [6, 3, 8, 9, 7] 3
# [7, 6, 3, 8, 9] 4
# [8, 9, 7, 6, 3] 6
# [3, 8, 9, 7, 6] 7
# [6, 3, 8, 9, 7] 8
# [7, 6, 3, 8, 9] 9
