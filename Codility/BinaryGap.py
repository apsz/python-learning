#!/usr/bin/python3

# 100% score
import re
def solution(N):
    str_N = str(bin(N))
    matches = re.findall(r'(?=(1[0]+1))', str_N)
    return len(min(matches))-2 if matches else 0

# import re
# def solution(N):
#     str_N = str(bin(N))
#     print(str_N)
#     if re.search('[1]0*[1]', str_N):
#         return max([len(x) for x in str_N.split('1')
#                     if all([k == '0' for k in x])])
#     return 0

# import re
# def solution(N):
#     str_N = str(bin(N))
#     matches = re.findall(r'(?=(1[0]+1))', str_N)
#     return len(min(matches))-2 if matches else 0
#     # results = [len(str(match.group(1))) for match in matches]
#     # return max(results)-2 if results else 0
#
# print(solution(15))
# print(solution(328))
# # print(solution(1965))
# print(solution(2))
# print(solution(66561))