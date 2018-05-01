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
	nnet = MLPClassifier(activation='relu', alpha=0.00001, \
				hidden_layer_sizes=(int(len(final_words)*0.05), \
				int(len(final_words)*0.025)),solver='adam', max_iter=400, \
				verbose=10)
	'''
	nnet = MLPClassifier(activation='relu', alpha=0.00001, \
				hidden_layer_sizes=(int(len(final_words)*0.5), \
				int(len(final_words)*0.25)),solver='adam', max_iter=400, \
				verbose=10)
	'''
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
	days = [9,10,11,12,13,16,17,18,19,20,23,24,25,26,27]
	days = [9,10,11,12,13]
	
	tweets = loadBagOfWords('data/tweets_week1_AAPL.json')
	final_words = loadFinalWords('data/final_words_week1_AAPL.dat')
	nn, input_data, labels = neuralNet(tweets, final_words, 'AAPL')
	runPredictions(input_data, labels, nn)

if __name__=='__main__':
	main()


