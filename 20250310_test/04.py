# -*- coding: utf-8 -*-
# UTF-8 encoding when using korean
n, m = map(int, input().split())

M = []
for _ in range(n):
	M.append(list(map(int, input().split())))

direction = [
	(-1,-1), (0, -1), (1, -1),
	(-1, 0), (1, 0),
	(-1, 1), (0, 1), (1, 1)
]

cnt = 0
for j in range(n):
	for i in range(m):
		if M[j][i] != -1:
			continue

		for d in direction:
			dj = j + d[0]
			di = i + d[1]
			if not(0 <= dj < n and 0 <= di < m):
				continue
			if M[dj][di] == -1:
				continue

			M[dj][di] += 1
			cnt += 1

print(cnt)
