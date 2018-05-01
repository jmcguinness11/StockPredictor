# neural_net.py
# In this file we actually run a neural network on the tweet data.
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
	x = stock_price_functions.getLabel(ticker, month, day, hour)
	return x

#parses individual json file
def parseJSON(data, month, day, hour):
	global words
	results = collections.defaultdict(list)
	for tweet in data.itervalues():
		text = prepareSentence(tweet['text'])
		for word in text:
			try:
				all_word_dict[word] += 1
			except KeyError as ex:
				all_word_dict[word] = 1
			'''
			if word not in all_word_dict.keys():
				all_word_dict[word] = 1
			else:
				all_word_dict[word] += 1
			'''
		#all_words.extend(text)
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
					filename = 'tweets_{}_{}_{}_{}.dat'.format(month, day, hour, minute)
					print 'Compiling data from {}...'.format(filename)
					with open(filename, 'r') as f:
						try:
							data = json.load(f)
						except ValueError as err:
							print 'Error parsing file: {}'.format(filename)
							exit(1)
						#output_data += parseJSON(data, month, day, hour)
						file_results = parseJSON(data, month, day, hour)
						for ticker in file_results.iterkeys():
							if ticker != file_ticker:
								continue
							for tweet_info in file_results[ticker]:
								output_data[ticker].append(tweet_info)
						f.close()
	return output_data

# Function closely adapted from J. Knight
def createFinalWords():
	#distinct_words = set(all_words)

	low_threshold = 40
	high_threshold = 80

	final_words = []
	for word, count in all_word_dict.iteritems():
		if count >= low_threshold and count < high_threshold:
			final_words.append(word)
	return final_words

	#TODO -- remove
	'''
	counts = []
	final_words = []
	print len(distinct_words), len(all_words)
	for word in distinct_words:
		counts.append(all_words.count(word))
		if all_words.count(word) > low_threshold and all_words.count(word) < high_threshold: 
			final_words.append(word)
	counts = np.asarray(counts)
	print 'Percentiles: 10, 20, 40, 60, 80, 90'
	print np.percentile(counts,10), np.percentile(counts,20), np.percentile(counts,40), np.percentile(counts,60), np.percentile(counts,80), np.percentile(counts,90)
	return final_words
	'''

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
		for tweet_data in tweets[ticker]:
			tweet_data[0] = toBOW(tweet_data[0], final_words)
			result[ticker].append(tweet_data)
	return result

def main():
	days = [9,10,11,12,13,16,17,18,19,20,23,24,25,26,27]
	days = [9,10,11,12,13]
	tweets = loadData([4], days, 'AAPL')
	print 'Creating Final Words...'
	final_words = createFinalWords()
	tweets = tweetsToBagOfWords(tweets, final_words)
	tweet_file = 'data/tweets_week1_AAPL_48.json'
	final_word_file = 'data/final_words_week1_AAPL_48.dat'
	
	#Write to tweet file
	with open(tweet_file, 'w') as f:
		json.dump(tweets, f)
	
	#Write to final word file
	with open(final_word_file, 'w') as f:
		for word in final_words:
			f.write(word)
			f.write("\n")

if __name__=='__main__':
	main()


