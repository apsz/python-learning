#!/usr/bin/python3

# Python 2.7 division (/ doesnt mean float div)
# 100% score
import math
def solution(X, Y, D):
    return int(math.ceil(float(Y - X) / float(D)))

print(solution(10, 85, 30))