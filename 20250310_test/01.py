n = int(input())
layers = [ int(value) for value in input().split() ]

answer = 0

for i in range(1, n):
	answer = answer + (layers[i-1] * layers[i])



print(answer)
