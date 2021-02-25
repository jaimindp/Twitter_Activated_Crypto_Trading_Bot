import tweepy
import json
import time
from kraken_api import *
from datetime import datetime
import ast

# Checks if a tweet from a user contains a particular trigger word
def tweepy_pull(api, user, pair, crypto, hold_time, volume, simulate, wait_tweet=True, logfile=None):
	
	exchange = kraken_api(api_keys, logfile=logfile)

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
					new_tweet = api.user_timeline(user_id=user[1],
												  count=1,
												  include_rts = True,
												  exclude_replies = True,
												  tweet_mode = 'extended',
												  wait_on_rate_limit=True,
												  wait_on_rate_limit_notify=True
												  )[0]
					time.sleep(1)				
				except Exception as e:
					print(e,'\nTemporarily failed at tweet collector\n')
					print('\nWaiting for {} to tweet\n'.format(user[0]))

		else:
			new_tweet = {'full_text':'Fake tweet about dogecoin or something','created_at':datetime.now()}

		
		if not wait_tweet or any(i in new_tweet.full_text.lower() for i in crypto['triggers']):
			trigger_time = datetime.now()
			print('\nMoonshot inbound!  -  %s' % (trigger_time.strftime('%b %d - %H:%M:%S')))
			exchange.execute_trade(pair, hold_time=hold_time, buy_volume=volume, simulate=simulate)
			if wait_tweet:
				print('\nClosed out on Tweet: "%s" created at : %s\n' %(new_tweet.full_text, new_tweet.created_at.strftime('%b %d - %H:%M:%S')))
			else:
				print('\nClosed out on tweet at %s\n' %(datetime.now().strftime('%b %d - %H:%M:%S')))

# Loads a json file
def load_json(filepath):
	with open(filepath) as json_file:
		return json.load(json_file)

# Load keys, keywords and users
api_keys = load_json('../keys.json')
users = load_json('users.json')
cryptos = load_json('keywords.json')

twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}

# Use second group of twitter api keys
if '2' in sys.argv:	
	api_keys2 = load_json('../twitter_keys2.json')
	twitter_keys = {'consumer_key':api_keys2['twitter_keys']['consumer_key'],'consumer_secret':api_keys2['twitter_keys']['consumer_secret'],'access_token_key':api_keys2['twitter_keys']['access_token_key'],'access_token_secret': api_keys2['twitter_keys']['access_token_secret']}

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

pair = [buy_coin['symbol'], sell_coin['symbol']]

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
hold_time = [1]
if not skip_input:
	print('\nHodl time(s) seconds e.g. 200 or 30,60,90: ')
	hold_time = input()
	if not hold_time:
		hold_time = [30,60,90]
	
	hold_time = ast.literal_eval('['+hold_time+']')
	print(hold_time)

print('\nHodl time :'+'%.2fs '*len(hold_time) % tuple(hold_time))

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
simulate = True	
if not skip_input:
	print('\nTest y/n:')
	test = input()
	simulate = True
	if test == 'n': simulate = False

if simulate:
	print('\nSIMULATION TRADING')

# Inintilizing a file of jsons to log trades
logfile = False
if 'l' in sys.argv:
	logfile = True

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

# Execute function
tweepy_pull(api, user, pair, buy_coin, hold_time, volume, simulate, wait_tweet=not skip_input, logfile=logfile)