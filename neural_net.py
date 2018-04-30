# neural_net.py
# In this file we actually run a neural network on the tweet data.
# To write this file, we borrowed heavily from the following article:
# https://medium.com/@joshua_e_k/predicting-popular-tweets-with-python-and-neural-networks-on-a-raspberry-pi-71b63616c2f4

from sklearn.neural_network import MLPClassifier
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
	#print x
	return x

#parses individual json file
def parseJSON(data, month, day, hour):
	global words
	results = collections.defaultdict(list)
	for tweet in data.itervalues():
		text = prepareSentence(tweet['text'])
		all_words.extend(text)
		label = getStockLabel(tweet['company'], month, day, hour)
		results[tweet['company']].append([text,label])
	return results

def loadData(months, days):
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
							for tweet_info in file_results[ticker]:
								output_data[ticker].append(tweet_info)
						f.close()
	return output_data

# Function closely adapted from J. Knight
def createFinalWords():
	distinct_words = set(all_words)

	low_threshold = 12
	high_threshold = 34
	counts = []
	final_words = []
	print len(distinct_words), len(all_words)
	for word in distinct_words:
		print word
		counts.append(all_words.count(word))
		if all_words.count(word) > low_threshold and all_words.count(word) < high_threshold: 
			final_words.append(word)
	counts = np.asarray(counts)
	#print np.percentile(counts,65), np.percentile(counts,98)
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
		for tweet_data in tweets[ticker]:
			tweet_data[0] = toBOW(tweet_data[0], final_words)
			result[ticker].append(tweet_data)
	return result

#This will eventually be in a different file -- the actual neural net
def neuralNet(tweets, final_words):
	#Define and train the network
	nnet = MLPClassifier(activation='relu', alpha=0.0001, \
				hidden_layer_sizes=(int(len(final_words)*0.5), \
				int(len(final_words)*0.25)),solver='adam', max_iter=400, \
				verbose=10)
	#TODO - this is specific to apple
	tweets = tweets['AAPL']
	input_data = []
	output_data = []
	for tweet in tweets:
		input_data.append(tweet[0])
		output_data.append(tweet[1])
	print len(input_data), len(output_data)
	input_data = np.array(input_data)
	output_data = np.array(output_data)
	print input_data.shape, output_data.shape
	nnet.fit(input_data, output_data)
	return nnet, input_data

def runPredictions(data, nnet):
	for tweet in data:
		tweet = tweet.reshape(1,-1)
		print nnet.predict(tweet)

def main():
	days = [9,10,11,12,13,16,17,18,19,20,23,24,25,26,27]
	days = [9,10,11,12,13]
	days = [9]
	tweets = loadData([4], days)
	print 'Creating Final Words...'
	final_words = createFinalWords()
	tweets = tweetsToBagOfWords(tweets, final_words)
	#print json.dumps(tweets)
	nn, input_data = neuralNet(tweets, final_words)

	'''
	input_data = []
	for tweet in tweets['AAPL']:
		input_data.append(tweet[0])
	'''
	runPredictions(input_data, nn)

if __name__=='__main__':
	main()


