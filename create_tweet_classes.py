# create_tweet_classes.py
# this assumes the existence of a get_class(day, hour, ticker) function
# that returns the class (0, 1, or -1) for a given hour and ticker

import collections
import json

refined_tweets = collections.defaultdict(list)

#parses individual json file
def parseJSON(data):
	results = collections.defaultdict(int)
	for tweet in data.itervalues():
		if tweet['company'] in results: 
			results[tweet['company']] += 1
		else:
			results[tweet['company']] = 0
	print results
		

def loadData(months, days):
	hours = [10, 11, 12, 13, 14]
	minutes = [0, 15, 30, 45]
	for month in months:
		for day in days:
			for hour in hours:
				for minute in minutes:
					filename = 'tweets_{}_{}_{}_{}.dat'.format(month, day, hour, minute)
					with open(filename, 'r') as f:
						data = json.load(f)
						parseJSON(data)
						f.close()

def main():
	loadData([4], [10,11])

if __name__=='__main__':
	main()
