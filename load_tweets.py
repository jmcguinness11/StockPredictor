import json
filename = 'tweets_4_9_10_30.dat'

with open(filename) as f:
	d = json.load(f)
	print d['1111']
