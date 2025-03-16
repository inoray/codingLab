# -*- coding: utf-8 -*-
# UTF-8 encoding when using korean
n = int(input())
arr = list(map(int, input().split()))

total = sum(arr)
avg = total / n

diff_list = [a - avg for a in arr]

min_trans = int(sum(diff for diff in diff_list if diff > 0))

print(min_trans)
