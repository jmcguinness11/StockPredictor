# Here I experiment with the twitter streaming API
# This mostly follows the tutorial from 
# http://tweepy.readthedocs.io/en/v3.6.0/streaming_how_to.html

# Note - the fields in the Tweepy status class can be found at 
# https://gist.github.com/jaymcgrath/367c521f1dd786bc5a05ec3eeeb1cb04

import tweepy

#My stuff
class Tweet:
	def __init__(self, text, created_at):
		self.text = text
		self.created_at = None
		self.company_list = ['AAPL', 'XOM']
		self.company = None

	# Figure out what company the tweet was about
	def set_company(self):
		for company in self.company_list:
			if company.lower() in self.text.lower():
				self.company = company
				return True
		return False


#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
	
	def __init__(self):
		self.tweet_list = []
		self.api = None
	
	def set_api(self, api):
		self.api = api

	def on_status(self, status):
		tweet = Tweet(status.text, status.created_at)

		#ensure you're only adding tweets where the company can be deciphered
		if tweet.set_company():
			self.tweet_list.append(tweet)
		print(len(self.tweet_list)), status.text, tweet.company

	def on_error(self, status_code):
		if status_code == 420:
			return False #disconnects the stream

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
stream.filter(languages=["en"], track=['AAPL', 'XOM'])
