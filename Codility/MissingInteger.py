#!/usr/bin/python3

# 100% score
def solution(A):
    l = sorted(A)
    one = False
    if l[-1] < 0 or l[-1] == 0:
        return 1
    for i in range(1, l[0]):
        if i != l[0]:
            return i
    for i in range(len(l) - 1):
        x = l[i]
        y = l[i + 1]
        if x == 1:
            one = True
        if y == x:
            continue
        if y - x > 1:
            if x + 1 > 0:
                return x + 1
    if l[-1] > 1 and not one:
        return 1
    return l[-1] + 1

print(solution(list(range(10000))))
