import tweepy
import json
import time
from datetime import datetime
from binance_futures_api import * 


# Query using tweepy api
class Twitter_Query:
	def __init__(self, api, logfile=None, api2=None, print_timer=False):
		self.api = api
		self.logfile = logfile
		self.api2 = api2

	# query a user tweeting about a crypto
	def query(user,pair,crypto,hold_time, buy_volume,simulate,wait_tweet=True,print_timer=False):
		if wait_tweet:
			try:
				last_time = time.time()

				# Put in handling for errornous returns (if most recent tweet is not actually the most recent tweet)
				tweets = api.user_timeline(user_id = user[1], 
				                           count = 1,
				                           include_rts = True,
				                           exclude_replies = True,
				                           tweet_mode = 'extended',
				                           wait_on_rate_limit=True,
				                           wait_on_rate_limit_notify=True
				                           )
				last_tweet = new_tweet = first_tweet = tweets[0]
			except Exception as e:
				print('Couldnt get first tweet')
				continue
			print('\nWaiting for {} to tweet\n'.format(user[0]))
			
			# Loop and sleep for a second to check when the last tweet has changed (e.g. when user has tweeted)
			while new_tweet.full_text == last_tweet.full_text:
				if api2:
					api, api2 = api2, api
					if print_timer:
						print('\nTime between: %.6f' % (time.time() - last_time))
						print('Sleep time: %.4f' % (0.5-(time.time()-last_time)))
					sleep_time = 0.5 - (time.time() - last_time)
					time.sleep(max(0,sleep_time))
					last_time = time.time()

				else:
					if print_timer:
						print('\nTime between: %.6f' % (time.time() - last_time))
						print('Sleep time: %.4f' % (1-(time.time()-last_time)))
					sleep_time = 1-(time.time() - last_time)
					time.sleep(max(0, sleep_time))
					last_time = time.time()

				try:
					new_tweet = api.user_timeline(user_id = user[1],
						                          count = 1,
						                          include_rts = True,
						                          exclude_replies = True,
						                          tweet_mode = 'extended',
						                          wait_on_rate_limit=True,
						                          wait_on_rate_limit_notify=True
						                          )[0]
				except Exception as e:
					print(e,'\nTemporarily failed at tweet collector')
					print('\nWaiting for {} to tweet\n'.format(user[0]))
		# 	rt_flag = new_tweet.retweeted
		else:
			new_tweet = {'full_text':'Fake tweet about dogecoin or something','created_at':datetime.now()}
		# 	rt_flag = False

		# Check for any keywords in full text
		if (not wait_tweet or any(i in new_tweet.full_text.lower() for i in crypto['triggers'])) and not first_tweet.full_text == new_tweet.full_text:
			trigger_time = datetime.now()
			print('\nMoonshot inbound!  -  %s' % (trigger_time.strftime('%b %d - %H:%M:%S')))
			exchange.execute_trade(pair, hold_time=hold_time, buy_volume=volume, simulate=simulate)
			if wait_tweet:
				print('\nClosed out on Tweet: "%s" created at %s\n' %(new_tweet.full_text, new_tweet.created_at.strftime('%b %d - %H:%M:%S')))
			else:
				print('\nClosed out on tweet at %s\n' %(datetime.now().strftime('%b %d - %H:%M:%S')))
