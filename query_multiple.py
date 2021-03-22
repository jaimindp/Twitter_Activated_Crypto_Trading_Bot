import tweepy
import time
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from check_exchange import *
import threading
import re

# Query using tweepy self.api
class Twitter_Query:
	def __init__(self, api, users, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, buy_coin=None, log_file=None, full_ex=True, cancel=[False]):

		self.api = api
		self.users = users
		self.buy_coin = buy_coin
		self.sell_coin = sell_coin
		self.hold_times = hold_times
		self.buy_volume = buy_volume
		self.simulate = simulate
		self.exchange = exchange
		self.exchange_data = exchange_data
		self.log_file = log_file
		self.full_ex = full_ex
		self.base_tickers = set(['BTC','USDT','USDC','DAI','USD','GBP','EUR'])
		self.cancel = cancel

	# Returns a list of matches from CAPTIAL letter coin symbols of a user specified length 
	def substring_matches(self, text, num_letters, first=False):
		
		# First time check if $COIN is present with $ as the flag
		if first:
			# Special treatment for a special coin
			if 'DOGE' in text:
				return [['DOGE'], self.sell_coin]

			# Look for $ sign
			matches = re.findall('(?<=\$)[^\ ]+', text)
			if matches:
				return [matches, self.sell_coin]

		matches = re.findall('[A-Z]{%d}' % num_letters, text)
		
		# Finding the intersection but maintaining order
		ordered_matches = list(filter(lambda x : x not in self.base_tickers, matches))
		matches = [value for value in ordered_matches if value in self.exchange_data.cryptos]

		# Specific ticker of 1INCH symbol
		new_matches = []
		for i in range(len(matches)):
			if matches[i] == 'INCH':
				matches[i] = '1INCH'
			if matches[i] not in new_matches:
				new_matches.append(matches[i])

		return [new_matches, self.sell_coin]

	# Parse a tweet and execute trade
	def parse_tweet(self, new_tweet, utc_time):
		full_text = new_tweet.full_text

		if any(substr in full_text.lower() for substr in self.users[new_tweet.user.screen_name]['keywords']) and utc_time - new_tweet.created_at < timedelta(seconds=10):
			if self.full_ex: time.sleep(self.full_ex)
			# Handling a single coin without checking substrings
			if self.buy_coin:

				# Execute buy order
				try:
					pair = [self.buy_coin, self.sell_coin]
					coin_vol = self.exchange_data.buy_sell_vols[self.buy_coin]
					print('\n\n'+'*'*25 + ' Moonshot Inbound! '+'*'*25 + '\n')
					t = threading.Thread(target=self.exchange.execute_trade, args=(pair,), kwargs={'hold_times':self.hold_times, 'buy_volume':coin_vol, 'simulate':self.simulate})
					t.start()

				except Exception as e:
					print('\nTried executing trade with ticker %s/%s, did not work' % (self.buy_coin,self.sell_coin))
					print(e)
			
			else:	
				# Loop over possible coin string lengths and get coins, firstflag is the first try to trade, successful is a flag if traded or not
				firstflag, successful = True, False
				
				# String manipulation and finding coins
				full_text = full_text.replace('\n', ' ')
				full_text = full_text.replace('/',  ' ')
				for i in [3,4,5,2,6]:
					pairs = self.substring_matches(full_text, i, firstflag)
					firstflag = False
					if not pairs[0]:
						continue

					# Loop over the possible buy coins and try to trade
					# Currently will only execute 1 trade which is the first in the trade
					for j in range(len(pairs[0])):
						# Get coin volume from cached trade volumes and execute trade
						try:
							pair = [pairs[0][j], pairs[1]]
							coin_vol = self.exchange_data.buy_sell_vols[pair[0]]
							print('\n\n'+'*'*25 + ' Moonshot Inbound! '+'*'*25 + '\n')

							# Start the buy thread
							t = threading.Thread(target=self.exchange.execute_trade, args=(pair,), kwargs={'hold_times':self.hold_times, 'buy_volume':coin_vol, 'simulate':self.simulate})
							t.start()
							successful = True
							
							# Break means only execute on one coin
							break

						except Exception as e:
							print('\nTried executing trade with ticker %s, did not work' % str(pair))
							print(traceback.format_exc())
							print(e)
					if successful:
						break

				if not successful:
					print('\nNo valid tickers to trade in tweet')


	# query a user tweeting about a crypto
	def query(self, user, delay, print_timer=False):
		tz = get_localzone() # My current timezone
		error_count = 1

		while 1:
			try:
				last_time = time.time()

				# Put in handling for erroneous returns (if most recent tweet is not actually the most recent tweet)
				tweets = self.api.user_timeline(user_id = user['id'], 
				                           count = 1,
				                           include_rts = True,
				                           exclude_replies = True,
				                           tweet_mode = 'extended',
				                           wait_on_rate_limit=True,
				                           wait_on_rate_limit_notify=True
				                           )

				last_tweet = new_tweet = first_tweet = tweets[0]

			except Exception as e:
				print(e)
				print('\nCouldnt get first tweet')
				print('%s\n'%(datetime.now().strftime('%b %d - %H:%M:%S')))
				continue
			print('\nWaiting for {} to tweet\n'.format(user['username']))
			
			# Loop and sleep for a second to check when the last tweet has changed (e.g. when user has tweeted)
			while new_tweet.full_text == last_tweet.full_text:

				# Checking if the thread has been cancelled
				if self.cancel[0]:
					exit()
					
				local_time = tz.localize(datetime.now())
				utc_time = local_time.astimezone(pytz.utc).replace(tzinfo=None)
				if print_timer:
					print('\nTime between: %.6f' % (time.time() - last_time))
					print('Sleep time: %.4f' % (delay-(time.time()-last_time)))
				sleep_time = delay - (time.time() - last_time)
				time.sleep(max(0, sleep_time))
				last_time = time.time()
				try:
					new_tweet = self.api.user_timeline(user_id = user['id'],
						                          count = 1,
						                          include_rts = True,
						                          exclude_replies = True,
						                          tweet_mode = 'extended',
						                          wait_on_rate_limit=True,
						                          wait_on_rate_limit_notify=True
						                          )[0]

				except Exception as e:
					if error_count % 50 == 0:
						print(e,'\nTemporarily failed at tweet collector for the 5000th time')
						print('%s\n'%(datetime.now().strftime('%b %d - %H:%M:%S')))
						print('\nWaiting for {} to tweet\n'.format(user['username']))
					error_count += 1

			# Parse and execute tweet under correct conditions
			try:
				self.parse_tweet(new_tweet, utc_time)
			except Exception as e:
				print(traceback.format_exc())


# Starts two threads, one which checks for prices to update the initial $ amount to the correct amount of coins or coin fractions          
def query_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, print_timer=False, log_file=None, buy_coin=None, full_ex=True, exchange_data=None, cancel=[False]):

	# Create an exchange object with the base coin
	if exchange_data is None:
		coin_subset = None
		if buy_coin:
			coin_subset = [buy_coin]

		# Start price checking daemon thread
		exchange_data = exchange_pull(exchange, hold_times, base_coin=sell_coin, coin_subset=coin_subset)
		daemon = threading.Thread(name='daemon', target=exchange_data.buy_sell_volumes, args=(buy_volume,20*60))
		daemon.setDaemon(True)
		daemon.start()
		time.sleep(3)

	try:
		# Calculate delay 
		delay = len(users)
		querys = Twitter_Query(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, exchange_data, log_file=log_file, full_ex=full_ex, cancel=cancel)

		# Check for tweets from a user
		for user, v in users.items():
			# Create a thread for each user here
			t = threading.Thread(target=querys.query, args=({'username':user,'id':v['id']}, delay), kwargs={'print_timer':print_timer})
			t.start()
			
	except Exception as e:
		print(e)

