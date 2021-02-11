import tweepy
import json
import time
from datetime import datetime
from binance_api import *

# Checks if a tweet from a user contains a particular trigger word
def tweepy_pull(api, user, pair, crypto, hold_time, volume, simulate, wait_tweet=True, logfile=None):

	exchange = binance_api(api_keys, logfile=logfile)

	while 1:
		
		# Bypass the need to check twitter for testing if tweet = False
		if wait_tweet:
			try:
				tweets = api.user_timeline(user_id=user[1], 
				                           count=1,
				                           include_rts = True,
				                           exclude_replies = True,
				                           tweet_mode = 'extended',
				                           wait_on_rate_limit=True,
				                           wait_on_rate_limit_notify=True
				                           )
			except Exception as e:
				print('couldnt get first tweet')
				continue
			last_tweet = new_tweet = tweets[0]
			print('\nWaiting for {} to tweet\n'.format(user[0]))

			while new_tweet.full_text == last_tweet.full_text:
				try:
					new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], include_rts=True, exclude_replies=True, tweet_mode="extended", count=1,wait_on_rate_limit=True,wait_on_rate_limit_notify=True).items(1))[0]	
				except Exception as e:
					print(e,'\nFailed at tweet collector\n')
				time.sleep(1)


		if not wait_tweet or any(i in new_tweet.full_text.lower() for i in crypto['triggers']):
			print('\nMoonshot inbound!')
			exchange.execute_trade(pair, hold_time=hold_time, buy_volume=volume, simulate=simulate)
			print('\nClosed out\n')

		# if not wait_tweet:
			# exit()

# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}

# User and crypto selection
users ={'elon':['elonmusk',44196397], 'me':['ArbitrageDaddy', 1351770767130673152]} 
cryptos = {'doge':{'triggers':['doge',' ','hodl','doggo'],'symbol':'DOGE'}, \
		   'btc':{'triggers':['bitcoin', 'btc',' crypto', 'buttcoin'],'symbol':'BTC'},\
		   'usd':{'symbol':'USD'},'usdt':{'symbol':'USDT'},'gbp':{'symbol':'GBP'}}

# Get user inputs
print('\nEnter crypto to buy: '+'%s '* len(cryptos) % tuple(cryptos.keys()))
skip_input = False

# Buy currency
crypto  = input()
if not crypto:
	crypto = 'doge'
	skip_input = True
buy_coin = cryptos[crypto]

# Sell currency
if not skip_input:
	print('\nEnter currency to sell: '+'%s '* len(cryptos) % tuple(cryptos.keys()))
	sell_coin  = cryptos[input()]
else:
	sell_coin = cryptos['btc']

pair = [buy_coin['symbol'],sell_coin['symbol']]

# User to track
if not skip_input:
	print('\nUser: '+'%s '* len(users) % tuple(users.keys())) 
	username = input()
	if username:
		user = users[username]
	else:
		user = users['me']
		skip_input = True
else:
	user = users['me']

# Time after buying before selling
if not skip_input:
	print('\nHodl time (s): ')
	hold_time = input()
	if not hold_time:
		hold_time = 60
	else:
		hold_time = float(hold_time)
else:
	hold_time = 1

print('\nHodl time : %.2fs' % hold_time)

# Amount of crypto to buy (Fastest if fewest queries before buying)
if not skip_input:
	print('\nVolume in crypto: ')
	volume = input()
	if not volume:
		if crypto == 'doge':
			volume = 100
		elif crypto == 'btc':
			volume = 0.0002
	else:
		volume = float(volume)
else:
	volume = 50
print('\nVolume %.8f %s' % (volume, buy_coin['symbol']))

# Simulation trade or real trade
if not skip_input:
	print('\nTest y/n:')
	test = input()
	simulate = True
	if test == 'n': simulate = False
else:
	simulate = True

if simulate:
	print('\nSIMULATION TRADING')

# Inintilizing a file of jsons to log trades

# Command line argument : "python twitter_binance.py l" (log)
if 'l' in sys.argv:
	logfile = True
else:
	logfile = False

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

# Execute function
tweepy_pull(api, user, pair, buy_coin, hold_time, volume, simulate, wait_tweet=not skip_input, logfile=logfile)
