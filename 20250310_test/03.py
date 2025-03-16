# -*- coding: utf-8 -*-
# UTF-8 encoding when using korean
n = int(input())

arr = []
for _ in range(n):
	arr.append(list(map(int, input().split())))

x, y = map(int, input().split())

direction = [
	(-1,-1), (0, -1), (1, -1),
	(-1, 0), (0, 0), (1, 0),
	(-1, 1), (0, 1), (1, 1)
]

x -= 1
y -= 1
sum = 0
for d in direction:
	dx = x + d[0]
	dy = y + d[1]
	if not(0 <= dx < n and 0 <= dy < n):
		continue

	sum += arr[dy][dx]

print(sum)
