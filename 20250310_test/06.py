# -*- coding: utf-8 -*-
# UTF-8 encoding when using korean
import math

p, n = map(int, input().split())
data = {29900: 300, 34900: 1000, 39900: 2000, 49900: 6000, 59900: 11000, 69900: math.inf}

def better_plan(p, n):
	f = list(data.keys())
	dn = list(data.values())
	data_range = []
	f.sort()

	for i in range(len(f) -1):
		excess = (f[i+1] - f[i]) / 20
		data_range.append(dn[i] + excess)

	for i in range(len(data_range)):
		if n <= data_range[i]:
			return f[i]

	return f[-1]

def calc(p, n):
	if p == 69900:
		return p

	limit = data[p]

	if n <= limit:
		return p

	excess = n - limit

	if (excess >= 1250) and (excess < 5000):
		return p + 25000
	else:
		return p + min([20*excess, 180000])

better = better_plan(p,n)
print(better, end=' ')
print(calc(p,n), end=' ')
print(calc(better,n))
