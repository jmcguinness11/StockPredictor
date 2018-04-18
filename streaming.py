# Here I experiment with the twitter streaming API
# This mostly follows the tutorial from 
# http://tweepy.readthedocs.io/en/v3.6.0/streaming_how_to.html

# Note - the fields in the Tweepy status class can be found at 
# https://gist.github.com/jaymcgrath/367c521f1dd786bc5a05ec3eeeb1cb04

import tweepy
import json
import datetime
import time

ROOT = '/root/StockPredictor/'

# Create dictionary of companies and identifiers
my_company_dict = {'MMM': ['3M', 'MMM stock'], \
				'AXP': ['AXP', 'American Express', 'Amex'], \
				'BA': ['BA stock', 'Boeing'], \
				'CAT': ['CAT stock', 'Caterpillar inc', 'CaterpillarInc'], \
				'CVX': ['CVX', 'Chevron'], \
				'KO': ['KO stock', 'Coca-Cola', 'Coca Cola', 'Diet Coke'], \
				'DIS': ['DIS stock', 'Disney'], \
				'DWDP': ['DWDP', 'DowDuPont', 'Dow Chemical'], \
				'XOM': ['XOM', 'Exxon', 'Mobil'], \
				'GE': ['GE stock', 'General Electric'], \
				'GS': ['GS stock', 'Goldman'], \
				'HD': ['HD stock', 'Home Depot'], \
				'IBM': ['IBM'], \
				'INTC': ['INTC', 'Intel', 'i7'], \
				'JNJ': ['JNJ', 'Johnson & Johnson', 'a family company', 'Johnson and Johnson'], \
				'JPM': ['JPM', 'JPMorgan', 'Chase', 'JP Morgan'], \
				'MCD': ['MCD', 'McDonald\'s', 'mcdonalds', 'McD\'s', 'mcds'], \
				'NKE': ['NKE', 'Nike', 'AirJordan', 'Converse'], \
				'PFE': ['PFE', 'Pfizer'], \
				'AAPL': ['AAPL', 'Apple', 'Mac', 'Tim Cook'], \
				'PG': ['PG stock', 'Procter and Gamble', 'P&G', 'procter & gamble', 'Gilette', \
								'Olay', 'Oral-B', 'Pampers'], \
				'TRV': ['TRV', 'travelers.com', 'travelers stock', 'travelers insurance'], \
				'UTX': ['UTX', 'United Technologies', 'Pratt & Whitney'], \
				'UNH': ['UNH stock', 'UnitedHealth', 'United Health'], \
				'VZ': ['VZ', 'Verizon', 'fios'], \
				'V': ['Visa'], \
				'WMT': ['WMT', 'Walmart'], \
				'MSFT': ['MSFT', 'Microsoft'], \
				'MRK': ['MRK', 'Merck'], \
				'CSCO': ['CSCO', 'Cisco'] \
				}
#turn this into usable form
company_dict = {}
for key, val_list in my_company_dict.iteritems():
	for val in val_list:
		company_dict[val] = key

#My stuff
class Tweet:
	def __init__(self, text, created_at):
		self.text = text
		self.created_at = str(created_at)
		self.company = None

	# Figure out what company the tweet was about
	def set_company(self):
		for company in company_dict.keys():
			if company.lower() in self.text.lower():
				self.company = company_dict[company]
				return True
		return False
	
	def to_dict(self):
		result = {}
		result['text'] = self.text
		result['time'] = self.created_at
		result['company'] = self.company
		return result


#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
	
	def __init__(self):
		self.tweet_list = []
		self.api = None
		now = datetime.datetime.now()
		self.filename = '{}tweets_{}_{}_{}_{}.dat'.format(ROOT, now.month, now.day, now.hour-4, now.minute)
	
	def set_api(self, api):
		self.api = api
	
	def on_status(self, status):
		#exclude retweets and attempt to exclude pornography
		if 'RT @' in status.text or 'porn' in status.text.lower():
			return
		tweet = Tweet(status.text, status.created_at)

		#ensure you're only adding tweets where the company can be deciphered
		if tweet.set_company():
			self.tweet_list.append(tweet)
		
		#guard against printing weird characters
		try:
			print(len(self.tweet_list)), status.text, tweet.company
		except:
			pass
		
		if len(self.tweet_list) and not len(self.tweet_list) % 200:
			self.write_json()

	def on_error(self, status_code):
		if status_code == 420:
			print 'couldnt open'
			return False #disconnects the stream
	
	def write_json(self):
		tweets = {}
		for idx in range(len(self.tweet_list)):
			tweets[idx] = self.tweet_list[idx].to_dict()
		with open(self.filename, 'wb+') as outfile:
			json.dump(tweets, outfile)
			

# Authentication
customer_key = 'ISwBauCqacDzTkknltrnqH5AF'
customer_secret = 'IEWjwSbh05eIrCn5R0Al7zIh4yrasZonDfEI49haE6r3OqLOFz'
access_token = '975739019022696450-nRZj1dvokIf921TPnL0Gve2ziErfwaq'
access_token_secret = 'Rsi6PKXC7YjukZwXJ0n5e0TiRUsOnaU8XOOzJW9lGjbcu'
auth = tweepy.OAuthHandler(customer_key, customer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# Create a stream
my_listener = MyStreamListener()
my_listener.set_api(api)
stream = tweepy.Stream(auth = api.auth, listener=my_listener)
stream.filter(languages=["en"], track=company_dict.keys())
