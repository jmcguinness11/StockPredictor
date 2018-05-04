# preprocess_data.py
# In this file we begin to prepare our data to be run through the neural
# network by creating the list of final words that will be used to create
# the binary vectors that will represent the tweets in the network.
# To write this file, we borrowed heavily from the following article:
# https://medium.com/@joshua_e_k/predicting-popular-tweets-with-python-and-neural-networks-on-a-raspberry-pi-71b63616c2f4

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import re
from operator import itemgetter
import stock_price_functions
import collections
import json
import numpy as np
import random
import sys

# global variable for words
all_words = []
all_word_dict = {}

# Function by J. Knight
def prepareSentence(s):
	stemmer = LancasterStemmer()
	ignore_words = set(stopwords.words('english'))
	regpattern = re.compile('[\W_]+" "')
	s = re.sub('[^A-Za-z ]+', '', s)
	words = nltk.word_tokenize(s.lower())
	return [stemmer.stem(w.lower()) for w in words if w not in ignore_words and 'http' not in w]

#returns label for company and time
def getStockLabel(ticker, month, day, hour):
	return stock_price_functions.getLabel(ticker, month, day, hour)

#parses individual json file
def parseJSON(data, month, day, hour, ticker):
	global words
	results = collections.defaultdict(list)
	for tweet in data.itervalues():
		text = prepareSentence(tweet['text'])
		if tweet['company'] != ticker:
			continue
		for word in text:
			try:
				all_word_dict[word] += 1
			except KeyError as ex:
				all_word_dict[word] = 1
		label = getStockLabel(tweet['company'], month, day, hour)
		results[tweet['company']].append([text,label])
	return results

def loadData(months, days, file_ticker):
	hours = [10, 11, 12, 13, 14]
	minutes = [0, 15, 30, 45]
	output_data = collections.defaultdict(list)
	for month in months:
		for day in days:
			for hour in hours:
				for minute in minutes:
					filename = 'tweets/tweets_{}_{}_{}_{}.dat'.format(month, day, hour, minute)
					print 'Compiling data from {}...'.format(filename)
					with open(filename, 'r') as f:
						try:
							data = json.load(f)
						except ValueError as err:
							print 'Error parsing file: {}'.format(filename)
							exit(1)
						file_results = parseJSON(data, month, day, hour, file_ticker)
						for ticker in file_results.iterkeys():
							if ticker != file_ticker:
								continue
							for tweet_info in file_results[ticker]:
								output_data[ticker].append(tweet_info)
						f.close()
	return output_data

# Function closely adapted from J. Knight
def createFinalWords():

	#calculate threshold
	K = len(all_word_dict)
	t = 5000./K
	print K, t
	low_threshold = 20. / t
	print 'threshold:', low_threshold

	final_words = []
	for word, count in all_word_dict.iteritems():
		if count >= low_threshold:
			final_words.append(word)
	return final_words

# Function directly from J. Knight
def toBOW(sentence, words):
	bag = []
	for word in words:
		bag.append(1) if word in sentence else bag.append(0)
	return bag

# Function adapted from J. Knight
def tweetsToBagOfWords(tweets, final_words):
	result = collections.defaultdict(list)
	for ticker in tweets.iterkeys():
		total = len(tweets[ticker])
		curr = 0
		firstprint = False
		secondprint = False
		thirdprint = False
		for tweet_data in tweets[ticker]:
			tweet_data[0] = toBOW(tweet_data[0], final_words)
			#get rid of tweets with no matches
			if sum(tweet_data[0] != 0):
				result[ticker].append(tweet_data)

			pct_done = 1.*curr/total 
			if not firstprint and pct_done >= .25:
				print 'Progress: {}'.format(pct_done)
				firstprint = True
			elif not secondprint and pct_done >= .5:
				print 'Progress: {}'.format(pct_done)
				secondprint = True
			elif not thirdprint and pct_done >= .75:
				print 'Progress: {}'.format(pct_done)
				thirdprint = True

			curr += 1
	return result

def main():

	#ticker is a command line arg
	ticker = sys.argv[1]

	#tuesday and thursday of each week
	days = [10,12,17,19,24,26]
	tweets = loadData([4], days, ticker)
	
	print 'Creating Final Words...'
	final_words = createFinalWords()

	final_word_file = 'data/final_words_{}.dat'.format(ticker)

	#Write to final word file
	with open(final_word_file, 'w') as f:
		for word in final_words:
			f.write(word)
			f.write("\n")

if __name__=='__main__':
	main()


