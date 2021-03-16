import tweepy
import time
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from check_exchange import *
import threading

# Query using tweepy self.api
class Twitter_Query:
	def __init__(self, api, exchange, exchange_data):
		self.api = api
		self.exchange = exchange
		self.exchange_data = exchange_data

	# query a user tweeting about a crypto
	def query(self,user,pair,crypto,hold_time,volume,simulate,wait_tweet=True,print_timer=False,full_ex=True):
		tz = get_localzone() # My current timezone
		error_count = 1

		while 1:
			if wait_tweet:
				try:
					last_time = time.time()

					# Put in handling for errornous returns (if most recent tweet is not actually the most recent tweet)
					tweets = self.api.user_timeline(user_id = user[1], 
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
				print('\nWaiting for {} to tweet\n'.format(user[0]))
				
				# Loop and sleep for a second to check when the last tweet has changed (e.g. when user has tweeted)
				while new_tweet.full_text == last_tweet.full_text:
					local_time = tz.localize(datetime.now())
					utc_time = local_time.astimezone(pytz.utc).replace(tzinfo=None)
					if print_timer:
						print('\nTime between: %.6f' % (time.time() - last_time))
						print('Sleep time: %.4f' % (1-(time.time()-last_time)))
					if not full_ex:
						sleep_time = 1-(time.time() - last_time)
						time.sleep(max(0, sleep_time))
						last_time = time.time()

					try:
						new_tweet = self.api.user_timeline(user_id = user[1],
							                          count = 1,
							                          include_rts = True,
							                          exclude_replies = True,
							                          tweet_mode = 'extended',
							                          wait_on_rate_limit=True,
							                          wait_on_rate_limit_notify=True
							                          )[0]
						if full_ex:
							sleep_time = 1-(time.time() - last_time)
							time.sleep(max(0, sleep_time))
							last_time = time.time()

					except Exception as e:
						if error_count % 50 == 0:
							print(e,'\nTemporarily failed at tweet collector for the 5000th time')
							print('%s\n'%(datetime.now().strftime('%b %d - %H:%M:%S')))
							print('\nWaiting for {} to tweet\n'.format(user[0]))
						error_count += 1
			else:
				new_tweet = {'full_text':'Fake tweet about dogecoin or something','created_at':datetime.now()}

			# Check for any keywords in full text
			if (not wait_tweet or any(i in new_tweet.full_text.lower() for i in crypto['triggers'])) and not first_tweet.full_text == new_tweet.full_text  and utc_time - new_tweet.created_at < timedelta(seconds=10):
				trigger_time = datetime.now()
				print('\nMoonshot inbound!  -  %s' % (trigger_time.strftime('%b %d - %H:%M:%S')))
				coin_vol = self.exchange_data.buy_sell_vols[pair[0]]
				self.exchange.execute_trade(pair, hold_times=hold_time, buy_volume=coin_vol, simulate=simulate)
				if wait_tweet:
					print('\nClosed out on Tweet: "%s" created at %s\n' %(new_tweet.full_text, new_tweet.created_at.strftime('%b %d - %H:%M:%S')))
				else:
					print('\nClosed out on tweet at %s\n' %(datetime.now().strftime('%b %d - %H:%M:%S')))


# Starts two threads, one which checks for prices to update the initial $ amount to the correct amount of coins or coin fractions          
def query_tweets(api,exchange,user,pair,crypto,hold_times,buy_volume,simulate,wait_tweet=True,print_timer=False,full_ex=True):

	# Create an exchange object with the base coin
	coin_subset = [pair[0]]
	exchange_data = exchange_pull(exchange, hold_times, base_coin=pair[1], coin_subset=coin_subset)

	try:
		# Start price checking daemon thread
		daemon = threading.Thread(name='daemon', target=exchange_data.buy_sell_volumes, args=(buy_volume,20*60))
		daemon.setDaemon(True)
		daemon.start()
		time.sleep(3)

		# Check for tweets from a user
		querys = Twitter_Query(api, exchange, exchange_data)
		querys.query(user, pair, crypto, hold_times, buy_volume, simulate, wait_tweet, print_timer, full_ex=full_ex)

	except KeyboardInterrupt as e:
		print('\nKeyboard interrupt handling:\n\nExiting')
		exit()

