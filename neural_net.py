# neural_net.py
# In this file we actually run a neural network on the tweet data.

from sklearn.neural_network import MLPClassifier
import json
import sys
import numpy as np
import preprocess_data

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
	

#The actual neural net
def neuralNet(tweets_arrays, final_words, ticker):
	#Define and train the network
	nnet = MLPClassifier(activation='relu', alpha=0.00001, \
				hidden_layer_sizes=(int(len(final_words)*0.6), \
				int(len(final_words)*0.3)),solver='adam', max_iter=4000, \
				verbose=10)
	input_data = []
	output_data = []
	for tweets_array in tweets_arrays:
		tweets = tweets_array[ticker]
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

def runPredictions(data, label, nnet):
	numCorrect = 0
	cts = [0,0,0]
	for k in range(len(data)):
		tweet = data[k][0]
		tweet = np.asarray(tweet).reshape(1, -1)
		pred = nnet.predict(tweet)[0]
		cts[pred+1] += 1
		if pred == label:
			numCorrect += 1

	print 'Predictions: {}\tActual: {}'.format(cts, label)
	return numCorrect, len(data), cts

def main():
	#ticker and test week are command line args
	ticker = sys.argv[1]
	test_week = int(sys.argv[2])

	train1 = (test_week) % 3 + 1
	train2 = (test_week+1) % 3 + 1

	#calculate training days and testing days
	days = [9,10,11,12,13,16,17,18,19,20,23,24,25,26,27]
	begin_idx = test_week-1
	test_days = days[5*begin_idx:5*begin_idx+5]
	days = days[0:5*begin_idx] + days[5*begin_idx+5:]

	tweets_train1 = loadBagOfWords('data/tweets_week{}_{}.json'.format(train1,ticker))
	tweets_train2 = loadBagOfWords('data/tweets_week{}_{}.json'.format(train2,ticker))
	final_words = loadFinalWords('data/final_words_{}.dat'.format(ticker))
	nn, input_data, labels = neuralNet([tweets_train1, tweets_train2], final_words, ticker)

	correct_total = 0
	count_total = 0
	cts_total = [0,0,0]
	labels_total = [0,0,0]
	cts_correct = [0,0,0]
	for day in test_days:
		for hour in [10, 11, 12, 13, 14]:
			tweets_test = preprocess_data.loadData([4], [day], ticker, [hour])
			tweets_test = preprocess_data.tweetsToBagOfWords(tweets_test, final_words)
			label = preprocess_data.getStockLabel(ticker, 4, day, hour)
			correct, count, cts = runPredictions(tweets_test[ticker], label, nn)

			#aggregate counts
			for k in range(len(cts_total)):
				cts_total[k] += cts[k]
			cts_correct[label+1] += cts[label+1]
			labels_total[label+1] += sum(cts)

			correct_total += correct
			count_total += count
			acc = correct * 1.0 / count
			print 'Accuracy for {}:00 hour on April {}: {}'.format(hour, day, acc)
	print 'Overall testing accuracy for week {}: {}'.format(test_week, correct_total * 1.0 / count_total)
	neg1_precision = 1.0*cts_correct[0]/cts_total[0]
	zero_precision = 1.0*cts_correct[1]/cts_total[1]
	one_precision = 1.0*cts_correct[2]/cts_total[2]
	neg1_recall = 1.0*cts_correct[0]/labels_total[0]
	zero_recall = 1.0*cts_correct[1]/labels_total[1]
	one_recall = 1.0*cts_correct[2]/labels_total[2]
	print 'Precision by class:\n\t-1:\t{}\n\t0:\t{}\n\t1:\t{}'.format(neg1_precision, zero_precision, one_precision)
	print 'Recall by class:\n\t-1:\t{}\n\t0:\t{}\n\t1:\t{}'.format(neg1_recall, zero_recall, one_recall)
	print 'Number of times each class was predicted', cts_total, cts_correct

if __name__=='__main__':
	main()
