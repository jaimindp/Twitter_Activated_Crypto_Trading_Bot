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
import threading

# Listener class
class Listener(StreamListener):
	def __init__(self, users, sell_coin, hold_time, buy_volume, simulate, exchange, exchange_data, log_file=None):
		super(Listener,self).__init__()
		self.users = users
		self.sell_coin = sell_coin
		self.hold_time = hold_time
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.exchange_data = exchange_data
		self.log_file = log_file

	# Code to run on tweet
	def on_status(self, status):
	
		# Tweets with mentions
		try:
			if not status.truncated:
				full_text = status.text
			else:
				full_text = status.extended_tweet['full_text']

			if status.entities['user_mentions']:
				return

			print('\n\n\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name, status.user.id_str))
			print(status.created_at)

			if any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']) and status.in_reply_to_status_id is None and status.retweeted is False:
				print('\n\nMoonshot Inbound!\n\n')
				
				# Get the trading pair and how much to buy
				four = re.search('[A-Z]{4}', full_text)
				if four:
					pair = [four[0], self.sell_coin]
				else:
					three = re.search('[A-Z]{3}', full_text)
					if three:
						pair = [three[0], self.sell_coin]
				if pair[0] == 'INCH':
					pair[0] = '1INCH'

				coin_vol = self.exchange_data.buy_vols[pair[0]]

				# Execute trade
				self.exchange.execute_trade(pair, hold_time=self.hold_time, buy_volume=coin_vol, simulate=self.simulate)

				if self.log_file:
					self.log_file.write(status)

		except Exception as e:
			print('\nError when handling tweet')
			print(e)

		print('\nRestarting stream')


	def on_error(self, status_code):
		print('Error in streaming: %d' % status_code)
		if status_code == 420:
			time.sleep(10)
		# return False

# Stream tweets
def stream_tweets(api, users, sell_coin, hold_time, buy_volume, simulate, exchange, log_file=None):
	
	exchange_data = exchange_pull(exchange)
	exchange_data.get_tickers()
	exchange_data.buy_volumes(buy_volume)
	
	listener = Listener(users, sell_coin, hold_time, buy_volume, simulate, exchange, exchange_data, log_file=log_file)
	stream = Stream(auth=api.auth, listener=listener,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	try:
		user_ids = [i['id'] for i in users.values()]


		print('\nStarting stream\n')
		t = threading.Thread(name='non-daemon', target=n)
		d = threading.Thread(name='daemon', target=d)

		d.setDaemon(True)

		d.start()
		t.start()


		stream.filter(follow=user_ids, is_async=True)

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
