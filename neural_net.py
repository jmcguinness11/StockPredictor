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
import collections
import json
import sys
import numpy as np

def loadFinalWords(wordfile):
	result = []
	with open(wordfile, 'r') as f:
		for line in f:
			result.append(line.strip())
	f.close()
	return result	

def loadBagOfWords(bagfile):
	with open(bagfile, 'r') as f:
		result = json.load(f)
		f.close()
		return result
	

#This will eventually be in a different file -- the actual neural net
def neuralNet(tweets, final_words, ticker):
	#Define and train the network
	#TODO -- we can change the input lengths
	#TODO -- we actually don't need to load in final_words at all
	#	  -- so we should figure out how to get its length from the tweet data
	nnet = MLPClassifier(activation='relu', alpha=0.00001, \
				hidden_layer_sizes=(int(len(final_words)*0.5), \
				int(len(final_words)*0.25)),solver='adam', max_iter=400, \
				verbose=10)
	tweets = tweets[ticker]
	input_data = []
	output_data = []
	for tweet in tweets:
		input_data.append(tweet[0])
		output_data.append(tweet[1])
	print len(input_data), len(output_data)
	input_data = np.array(input_data)
	output_data = np.array(output_data)
	randomizer = np.random.permutation(input_data.shape[0])
	input_data = input_data[randomizer]
	output_data = output_data[randomizer]
	print input_data.shape, output_data.shape
	nnet.fit(input_data, output_data)
	return nnet, input_data, output_data

def runPredictions(data, labels, nnet):
	numCorrect = 0
	cts = [0,0,0]
	for k in range(len(data)):
		tweet = data[k]
		label = labels[k]
		tweet = tweet.reshape(1,-1)
		pred = nnet.predict(tweet)[0]
		print pred, label
		cts[label+1] += 1
		if pred == label:
			numCorrect += 1
		print cts
	
	print 'Acc: {}'.format(numCorrect*1.0/len(data))

def main():
	#ticker and test week are command line args
	ticker = sys.argv[1]
	#test_week = sys.argv[2]
	test_week = 1 #TODO - remove hardcoding

	train1 = (test_week) % 3 + 1
	train2 = (test_week+1) % 3 + 1

	#calculate training days and testing days
	days = [9,10,11,12,13,16,17,18,19,20,23,24,25,26,27]
	begin_idx = test_week-1
	test_days = days[5*begin_idx:5*begin_idx+5]
	days = days[0:5*begin_idx] + days[5*begin_idx+5:]
	
	'''
	tweets_train1 = loadBagOfWords('data/tweets_week{}_{}.json'.format(train1,ticker)
	tweets_train2 = loadBagOfWords('data/tweets_week{}_{}.json'.format(train2,ticker)
	tweets_test = loadBagOfWords('data/tweets_week{}_{}.json'.format(test_week,ticker)
	'''
	#TODO -- need to figure out how to merge the two training ones

	#TODO -- this is just for testing and wrong -- remove
	tweets_test = loadBagOfWords('data/tweets_week{}_{}.json'.format(test_week,ticker))
	tweets = tweets_test

	final_words = loadFinalWords('data/final_words_{}.dat'.format(ticker))
	nn, input_data, labels = neuralNet(tweets, final_words, ticker)

	#TODO -- input data will be different in testing
	#     -- (probably some sort of loop over the individual hours)
	runPredictions(input_data, labels, nn)

if __name__=='__main__':
	main()


