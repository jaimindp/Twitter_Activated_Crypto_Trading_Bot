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
import traceback

# Listener class
class Listener(StreamListener):
	def __init__(self, users, user_ids, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, buy_coin=None, log_file=None, full_ex=True):
		super(Listener,self).__init__()

		# Define variables for the class when listener is created
		self.users = users
		self.user_ids = user_ids
		self.buy_coin = buy_coin
		self.sell_coin = sell_coin
		self.hold_times = hold_times
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.exchange_data = exchange_data
		self.log_file = log_file
		self.full_ex = full_ex

	# Returns a pair of Coin symbol and base coin e.g. ['DOGE', 'BTC']
	def substring_match(self, text, num_letters, first=True):
		
		# First time check if $COIN is present with $ as the flag
		if first:
			text = text.replace('\n' , ' ')
			match = re.search('(?<=\$)[^\ ]+', text)
			if match:
				return [match[0], self.sell_coin]

		# Otherwise use the length of consecutive capital letters
		match = re.search('[A-Z]{%d}' % num_letters, text)
		if not match:
			return None

		match = match[0]
		# Specific ticker of 1INCH symbol
		if match == 'INCH':
			match = '1INCH'

		return [match, self.sell_coin]

	# Code to run on tweet
	def on_status(self, status):
	
		# Tweets with mentions
		try:
			# Handling extended vs not extended tweets
			if not status.truncated:
				full_text = status.text
			else:
				full_text = status.extended_tweet['full_text']

			if status.user.id not in self.user_ids:
				return

			print('\n\n'+'-'*25 + ' New Tweet ' + '-' * 25)
			print('%s\n\n%s \n\n@%s' % (datetime.now().strftime('%H:%M:%S'), full_text, status.user.screen_name))
			print('Created at: %s' %  status.created_at.strftime('%H:%M:%S - %b %d'))

			# Check for substring matches with the keywords speicified for that user and only looking at original non-retweets
			if any(substr in full_text.lower() for substr in self.users[status.user.screen_name]['keywords']) and status.in_reply_to_status_id is None and status.retweeted is False:
				if self.full_ex: time.sleep(full_ex)
				print('\n\n'+'*'*25 + ' Moonshot Inbound! '+'*'*25 + '\n')
				
				# Handling a single coin without checking substrings
				if self.buy_coin:

					# Execute buy order
					try:
						pair = [self.buy_coin, self.sell_coin]
						coin_vol = self.exchange_data.buy_sell_vols[self.buy_coin]
						self.exchange.execute_trade(pair, hold_times=self.hold_times, buy_volume=coin_vol, simulate=self.simulate)
					except Exception as e:
						print('\nTried executing trade with ticker %s/%s, did not work' % (self.buy_coin,self.sell_coin))
						print(e)
				else:
					# Loop from maximum coin name length to shortest coin name length 
					firstflag = True
					for i in range(6, 1, -1):
						pair = self.substring_match(full_text, i, firstflag)
						firstflag = False
						if not pair:
							continue
						try:
							# Get coin volume from cached trade volumes and execute trade
							coin_vol = self.exchange_data.buy_sell_vols[pair[0]]
							self.exchange.execute_trade(pair, hold_times=self.hold_times, buy_volume=coin_vol, simulate=self.simulate)
							break

						except Exception as e:
							print('\nTried executing trade with ticker %s, did not work' % pair[0])
							print(traceback.format_exc())
							print(e)

				# Log tweet
				if self.log_file:
					self.log_file.write(status)
			else:
				print('Trade not triggered')

		except Exception as e:
			print('\nError when handling tweet')
			print(e)

		print('\nRestarting stream\n')

	# Streaming error handling
	def on_error(self, status_code):
		print('Error in streaming: Code %d, sleeping for 10' % status_code)
		if status_code == 420:
			print('Wait for cooloff period to try again\n\nExiting')
			exit()
		time.sleep(10)
		print('\nRestarting stream\n')


# Stream tweets
def stream_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, keywords=None, log_file=None, buy_coin=None, full_ex=True):
	
	# Set and list of ids of users tracked
	user_ids_list = [i['id'] for i in users.values()]
	user_ids_set = [int(i) for i in user_ids_list]

	# Get exchange tickers and calculate volumes to buy for each tradeable crypto
	coin_subset = None
	if buy_coin:
		coin_subset = [buy_coin]

	exchange_data = exchange_pull(exchange, hold_times, base_coin=sell_coin, coin_subset=coin_subset)
	
	# Create the Tweepy streamer
	listener = Listener(users, user_ids_set, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, log_file=log_file, buy_coin=buy_coin, full_ex=full_ex)
	stream = Stream(auth=api.auth, listener=listener, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	# Start stream and query prices
	print('\nStarting stream\n')
	
	# Try catch for different termination procedures
	try:
		# Create daemon thread which exits when other thread exits
		d = threading.Thread(name='daemon', target=exchange_data.buy_sell_volumes, args=(buy_volume,20*60))
		d.setDaemon(True)
		d.start()

		# Start streaming tweets
		if keywords:
			stream.filter(follow=user_ids_list,track=keywords)
		else:
			stream.filter(follow=user_ids_list)
		
	# Keyboard interrupt kills the whole program
	except KeyboardInterrupt as e:
		stream.disconnect()
		print("\nStopped stream")
		exit()
	
	# Disconnect the stream and kill the thread looking for prices
	finally:
		print('\nDisconnected Stream\n')
		exchange_data.stopflag = True
		stream.disconnect()


