import tweepy
import json
import time
import ast
import os
from datetime import datetime
import traceback
from binance_api import *
from stream_multiple import *
from query import *

# Checks if a tweet from a user contains a particular trigger word
def tweepy_pull(api, users, sell_coin, hold_time, volume, simulate, stream, wait_tweet=True, logfile=None, print_timer=False, full_ex=True):

	exchange = binance_api(api_keys, logfile=logfile)

	# Stream tweets
	if stream:
		while 1:
			# user_ids = [i['id'] for i in users.values()]
			try:
				stream_tweets(api, users, sell_coin, hold_time, volume, simulate, exchange, full_ex=full_ex)
			except Exception as e:
				print(e)
				print(traceback.format_exc())
				print('%s\n'%(datetime.now().strftime('%b %d - %H:%M:%S')))
				time.sleep(10)
	
	# Query tweets
	else:
		twitter_q = Twitter_Query(api, exchange)	
		twitter_q.query(users, sell_coin, hold_time, volume, simulate, wait_tweet, print_timer)

# Loads a json file
def load_json(filepath):
	with open(filepath) as json_file:
		return json.load(json_file)

# Command line: python twitter_binance_futures.py l (save trade logs) p (print query intervals) 2 (2nd set of twitter keys)

# Load keys, keywords and users 
api_keys = load_json('../keys.json')
users = load_json('users.json')
cryptos = load_json('keywords.json')

if 'prev_trades' in os.listdir():
	full_ex = False
	exchange_keywords = load_json('exchange_jaimin_keywords.json')
	print("\nJP")
else:
	full_ex = True
	exchange_keywords = load_json('exchange_keywords.json')

twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}

# Use second group of twitter api keys
if '2' in sys.argv:
	api_keys2 = load_json('../twitter_keys2.json')
	twitter_keys = {'consumer_key':api_keys2['twitter_keys']['consumer_key'],'consumer_secret':api_keys2['twitter_keys']['consumer_secret'],'access_token_key':api_keys2['twitter_keys']['access_token_key'],'access_token_secret': api_keys2['twitter_keys']['access_token_secret']}

# Get user inputs
# Sell currency
print('\nEnter currency to sell: btc, usdt')
sell_input = input()
if not sell_input:
	sell_coin = 'BTC'
	skip_input = True
else:
	sell_coin  = cryptos[sell_input]['symbol']
	skip_input = False

# Users to track
if not skip_input:
	print('\nUsers: e.g. coinbase,CoinbasePro,binance from: '+'%s '* len(exchange_keywords) % tuple(list(exchange_keywords.keys())))
	usernames = input()
	if not usernames:
		users = ['ArbitrageDaddy']
		skip_input = True
	else:
		users = usernames.split(',')
else:
	users = ['ArbitrageDaddy']
users = {key:exchange_keywords[key] for key in users}

# Time after buying before selling
hold_time = [1]
if not skip_input:
	print('\nHodl time(s) seconds e.g. 200 or 30,60,90: ')
	hold_time = input()
	if not hold_time:
		hold_time = [30,60,90]
		skip_input = True
	else:
		hold_time = ast.literal_eval('['+hold_time+']')
	print(hold_time)

print('\nHodl time : '+'%.2fs '*len(hold_time) % tuple(hold_time))

# Amount in USD to buy
if not skip_input:
	print('\nVolume in USD: ')
	volume = input()
	if not volume:
		volume = 20
	else:
		volume = float(volume)
else:
	volume = 20
print('\nVolume %.2f USD' % (volume))

# Simulation trade or real trade
simulate = True	
if not skip_input:
	print('\nTest y/n:')
	test = input()
	simulate = True
	if test == 'n': simulate = False

# User to track, empty to skip tweet waiting
stream = True
if not skip_input:
	print('\nStream or query s/q: ')
	stream_input = input()
	if stream_input != 'q':
		stream = True
	else:
		stream = False

if simulate:
	print('\nSIMULATION TRADING\n')

# Inintilizing a file of jsons to log trades
logfile = False
if 'l' in sys.argv:
	logfile = True

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

# Execute function
tweepy_pull(api, users, sell_coin, hold_time, volume, simulate, stream, wait_tweet=not skip_input, logfile=logfile, full_ex=full_ex)


