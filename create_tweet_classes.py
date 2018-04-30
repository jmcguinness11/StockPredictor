# create_tweet_classes.py
# this assumes the existence of a get_class(day, hour, ticker) function
# that returns the class (0, 1, or -1) for a given hour and ticker

import collections
import json
import random

refined_tweets = collections.defaultdict(list)

#returns label for company and time
def getLabel(ticker, month, day, hour):
	return random.randint(-1,1)

#parses individual json file
def parseJSON(data, month, day, hour):
	results = []
	for tweet in data.itervalues():
		text = tweet['text']
		label = getLabel(tweet['company'], month, day, hour)
		results.append([text,label])
	return results

def loadData(months, days):
	hours = [10, 11, 12, 13, 14]
	minutes = [0, 15, 30, 45]
	output_data = []
	for month in months:
		for day in days:
			for hour in hours:
				for minute in minutes:
					filename = 'tweets_{}_{}_{}_{}.dat'.format(month, day, hour, minute)
					with open(filename, 'r') as f:
						try:
							data = json.load(f)
						except ValueError as err:
							print filename
							exit(1)
						output_data += parseJSON(data, month, day, hour)
						f.close()
	print len(output_data)
	print output_data[0:10]
	return output_data

def main():
	days = [9,10,11,12,13,16,17]
	loadData([4], days)

if __name__=='__main__':
	main()
