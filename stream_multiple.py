# Another method using streaming (mitigates the wait on rate limit issue)
import tweepy
import time
import json
import sys
from datetime import datetime
from tweepy import Stream
from tweepy.streaming import StreamListener
from check_exchange import *
import re

# Listener class
class Listener(StreamListener):
	def __init__(self, users, user_ids, sell_coin, hold_time, buy_volume, simulate, exchange, exchange_data, log_file=None):
		super(Listener,self).__init__()

		# Define variables for the class when listener is created
		self.users = users
		self.user_ids = user_ids
		self.sell_coin = sell_coin
		self.hold_time = hold_time
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.exchange_data = exchange_data
		self.log_file = log_file

	# Returns a pair of Coin symbol and base coin e.g. ['DOGE', 'BTC']
	def substring_match(self, text, num_letters):
		match = re.search('[A-Z]{%d}' %num_letters, text)
		if not match:
			return None

		# Specific ticker of 1INCH symbol
		if match[0] == 'INCH':
			match[0] = '1INCH'

		return [match[0], self.sell_coin]

	# Code to run on tweet
	def on_status(self, status):
	
		# Tweets with mentions
		try:
			if not status.truncated:
				full_text = status.text
			else:
				full_text = status.extended_tweet['full_text']

			if status.user.id not in self.user_ids:
				return

			print('\n\n\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name, status.user.id_str))
			print(status.created_at)

			if any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']) and status.in_reply_to_status_id is None and status.retweeted is False:
				print('\n\nMoonshot Inbound!\n\n')
				
				# Loop from maximum coin name length to shortest coin name length 
				for i in range(6, 2, -1):
					pair = self.substring_match(full_text, i)
					if not pair:
						continue
					try:
						# Get coin volume from cached trade volumes and execute trade
						coin_vol = self.exchange_data.buy_vols[pair[0]]
						self.exchange.execute_trade(pair, hold_time=self.hold_time, buy_volume=coin_vol, simulate=self.simulate)

						# If successful, break
						break

					except Exception as e:
						print('\nTried executing trade with ticker %s, did not work' % pair[0])
						print(e)

				# Log tweet
				if self.log_file:
					self.log_file.write(status)

		except Exception as e:
			print('\nError when handling tweet')
			print(e)

		print('\nRestarting stream\n')

	# Streaming error handling
	def on_error(self, status_code):
		print('Error in streaming: %d' % status_code)
		if status_code == 420:
			time.sleep(10)

# Stream tweets
def stream_tweets(api, users, sell_coin, hold_time, buy_volume, simulate, exchange, log_file=None):
	
	# Get exchange tickers and calculate volumes to buy for each tradeable crypto
	exchange_data = exchange_pull(exchange)
	exchange_data.get_tickers()
	exchange_data.buy_volumes(buy_volume)
	
	# Set of ids of users tracked
	user_ids = set([int(i['id']) for i in users.values()])

	# Create the Tweepy streamer
	listener = Listener(users, user_ids, sell_coin, hold_time, buy_volume, simulate, exchange, exchange_data, log_file=log_file)
	stream = Stream(auth=api.auth, listener=listener,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	try:
		print('\nStarting stream\n')
		stream.filter(follow=[str(i) for i in user_ids], is_async=True)

		# Work out amounts of trading pairs to get
		while 1:
			time.sleep(20*60) # Checks trading pairs at intervals
			exchange_data.get_tickers()
			exchange_data.buy_volumes(buy_volume)

	except KeyboardInterrupt as e:
		stream.disconnect()
		print("\nStopped stream")
		exit()
	finally:
		print('\nDone\n')
		stream.disconnect()
