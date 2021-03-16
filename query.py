import tweepy
import time
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone

# Query using tweepy self.api
class Twitter_Query:
	def __init__(self, api, exchange):
		self.api = api
		self.exchange = exchange

	# query a user tweeting about a crypto
	def query(self,user,pair,crypto,hold_time,volume,simulate,wait_tweet=True,print_timer=False):
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
				self.exchange.execute_trade(pair, hold_times=hold_time, buy_volume=volume, simulate=simulate)
				if wait_tweet:
					print('\nClosed out on Tweet: "%s" created at %s\n' %(new_tweet.full_text, new_tweet.created_at.strftime('%b %d - %H:%M:%S')))
				else:
					print('\nClosed out on tweet at %s\n' %(datetime.now().strftime('%b %d - %H:%M:%S')))
