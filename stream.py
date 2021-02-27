# Another method using streaming (mitigates the wait on rate limit issue)
import tweepy
import time
import json
import sys
from datetime import datetime
from tweepy import Stream
from tweepy.streaming import StreamListener

# Listener class
class Listener(StreamListener):
	def __init__(self, ids, keywords, pair, hold_time, buy_volume, simulate, exchange, log_file=None):
		super(Listener,self).__init__()
		self.ids = ids
		self.log_file = log_file
		self.keywords = keywords
		self.hold_time = hold_time
		self.pair = pair
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		
	# Code to run on tweet
	def on_status(self, status):
		if str(status.user.id_str) in self.ids:
			if not status.truncated:
				full_text = status.text
			else:
				full_text = status.extended_tweet['full_text']

			print('\n\n\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name, status.user.id_str))
			print(status.created_at)
			if any(word in full_text.lower() for word in self.keywords) and status.in_reply_to_status_id is None:
				print('\n\nMoonshot Inbound!\n\n')
				
				# Execute trade
				self.exchange.execute_trade(self.pair, hold_time=self.hold_time, buy_volume=self.buy_volume, simulate=self.simulate)
				
				if self.log_file:
					self.log_file.write(status)

			print('\nRestarting stream')

	def on_error(self, status_code):
		print(status_code)
		return False

# Stream tweets
def stream_tweets(api, users, id_set, pair, hold_time, buy_volume, simulate, exchange, keywords=None, log_file=None):
	
	listener = Listener(id_set, keywords, pair, hold_time, buy_volume, simulate, exchange, log_file=log_file)
	stream = Stream(auth=api.auth, listener=listener,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	try:
		print('\nStarting stream\n')
		stream.filter(follow=users, track=keywords)
		# stream.filter(follow=users, track=keywords, is_async=True)

	except KeyboardInterrupt as e:
		stream.disconnect()
		print("Stopped stream")
		exit()
	finally:
		print('Done')
		stream.disconnect()
