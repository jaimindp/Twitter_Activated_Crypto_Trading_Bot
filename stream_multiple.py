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
	def __init__(self, users, sell_coin, hold_time, buy_volume, simulate, exchange, log_file=None):
		super(Listener,self).__init__()
		self.users = users
		self.sell_coin = sell_coin
		self.hold_time = hold_time
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.log_file = log_file

	# Code to run on tweet
	def on_status(self, status):
	
		# Tweets with mentions
		if not status.truncated:
			full_text = status.text
		else:
			full_text = status.extended_tweet['full_text']

		if status.entities['user_mentions']:
			print('\n\n\n%s: with mentions %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name, status.user.id_str))
			print(status.created_at)
			return

		print('\n\n\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name, status.user.id_str))
		print(status.created_at)
		print(any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']))
		print(status.in_reply_to_status_id is None)
		print(status.retweeted is False)

		if any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']) and status.in_reply_to_status_id is None and status.retweeted is False:
			print('\n\nMoonshot Inbound!\n\n')
			
			# Get the trading pair and how much to buy

			# Execute trade
			self.exchange.execute_trade(pair, hold_time=self.hold_time, buy_volume=self.buy_volume, simulate=self.simulate)
			
			if self.log_file:
				self.log_file.write(status)

		print('\nRestarting stream')

	def on_error(self, status_code):
		print(status_code)
		return False

# Stream tweets
def stream_tweets(api, users, sell_coin, hold_time, buy_volume, simulate, exchange, log_file=None):
	
	listener = Listener(users, sell_coin, hold_time, buy_volume, simulate, exchange, log_file=log_file)
	stream = Stream(auth=api.auth, listener=listener,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	try:
		print('\nStarting stream\n')
		user_ids = [i['id'] for i in users.values()]
		stream.filter(follow=user_ids, is_async = True)
		
		# Work out amounts of trading pairs to get
		while 1:
			self.exchange.f
			time.sleep(1*60)
		# stream.filter(follow=users, track=keywords, is_async=True)

	except KeyboardInterrupt as e:
		stream.disconnect()
		print("Stopped stream")
		exit()
	finally:
		print('Done')
		stream.disconnect()
