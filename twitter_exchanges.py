import tweepy
import json
import time
import ast
import os
from datetime import datetime
import traceback
from binance_api import *
from stream_multiple import *
from query_multiple import *

# Checks if a tweet from a user contains a particular trigger word
def tweepy_pull(api, users, sell_coin, hold_times, buy_volume, simulate, stream, wait_tweet=True, logfile=None, print_timer=False, full_ex=True, both=False, account_json=None):

	# Create exchange object and start querying prices as a daemon (cancels when the main thread ends)
	exchange = binance_api(api_keys, logfile=logfile, block=both, account_json=account_json)
	exchange_data = exchange_pull(exchange, hold_times, base_coin=sell_coin)
	daemon = threading.Thread(name='daemon', target=exchange_data.buy_sell_volumes, args=(volume,20*60))
	daemon.setDaemon(True)
	daemon.start()
	time.sleep(3)

	# Stream tweets
	if not both:
		if stream:
			# From stream_multiple.py file
			stream_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, full_ex=full_ex, exchange_data=exchange_data)
		else:
			# Query tweets from query.py file
			query_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, print_timer=print_timer, full_ex=full_ex, exchange_data=exchange_data)
	else:
		# Start the query as a thread with cancellling mechanism
		cancel = [False]
		t1 = threading.Thread(target=query_tweets, args=(api, users, sell_coin, hold_times, buy_volume, simulate, exchange), kwargs={'print_timer':print_timer, 'full_ex':full_ex, 'exchange_data':exchange_data, 'cancel':cancel})
		t1.start()

		# Stream tweets
		stream_tweets(api, users, sell_coin, hold_times, buy_volume, simulate, exchange, full_ex=full_ex, exchange_data=exchange_data)

		print('\nSetting cancel to true')
		cancel[0] = True
		while threading.active_count() > 4 + len(users):
			print('\nThere are %d trades left to clear' %  (threading.active_count() - 4 - len(users)))
			time.sleep(20)
		print('Exiting, can finish')
		exit()


# Loads a json file
def load_json(filepath):
	with open(filepath) as json_file:
		return json.load(json_file)

def read_twitter_keys(keys):
	twitter_keys = {'consumer_key':keys['twitter_keys']['consumer_key'],'consumer_secret':keys['twitter_keys']['consumer_secret'],'access_token_key':keys['twitter_keys']['access_token_key'],'access_token_secret': keys['twitter_keys']['access_token_secret']}
	return twitter_keys

# Command line: python twitter_binance_futures.py l (save trade logs) p (print query intervals) 2 (2nd set of twitter keys)

# Load keys, keywords and users 
api_keys = load_json('../keys.json')
cryptos = load_json('keywords.json')
twitter_keys = read_twitter_keys(api_keys)



# Get command line user inputs
full_ex = True
if 'prev_trades' in os.listdir():
	json_files = list(filter(lambda x : x.endswith('.json') and x not in ['keywords.json','users.json'],os.listdir()))
	print('\nChoose accounts to follow: '+'%s  ' * len(json_files) % tuple([file+' ('+str(i)+') ' for i, file in enumerate(json_files)]))
	accounts = input()
	full_ex = False
	account_json_str = json_files[int(accounts)]
	exchange_keywords = load_json(account_json_str)
else:
	account_json_str = 'exchange_keywords.json'
	exchange_keywords = load_json(account_json_str)


# Users to track
print('\nUsers: e.g. "coinbase,CoinbasePro,binance" or "all" from: '+'%s '* len(exchange_keywords) % tuple(list(exchange_keywords.keys())))
usernames = input()
skip_input = False
if not usernames:
	users = ['ArbitrageDaddy']
	skip_input = True
elif usernames == 'all':
	users = list(filter(lambda x : x not in ['ArbitrageDaddy', 'elonmusk'],[i for i in exchange_keywords.keys()]))
else:
	users = usernames.split(',')
print(users)
users = {key:exchange_keywords[key] for key in users}

# Sell currency
print('\nEnter currency to sell: btc, usdt')
sell_coin = 'BTC'
if not skip_input:
	sell_input = input()
	if not sell_input:
		sell_coin = 'BTC'
		skip_input = True
	else:
		sell_coin  = cryptos[sell_input]['symbol']
		skip_input = False


# Time after buying before selling
hold_time = [5]
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
stream, both = True, False
if not skip_input:
	print('\nStream or query s/q: ')
	stream_input = input()
	if stream_input == 'b':
		both = True
	elif stream_input != 'q':
		stream = True
	else:
		stream = False

# Alternating use of twitter api keys
if '2' in sys.argv:
	api_keys_2 = load_json('../twitter_keys2.json')	
	print('\nUsing twitter keys 2')
	twitter_keys = read_twitter_keys(api_keys_2)
elif '3' in sys.argv:
	api_keys_3 = load_json('../twitter_keys3.json')
	print('\nUsing twitter keys 3')
	twitter_keys = read_twitter_keys(api_keys_3)


if simulate:
	print('\n'+'-'*10+'  SIMULATION TRADING  '+'-'*10+'\n')
else:
	print('\n'+'-'*10+'  LIVE TRADING  '+'-'*10+'\n')

# Inintilizing a file of jsons to log trades
logfile = False
if 'l' in sys.argv:
	logfile = True

print_timer = False
if 'p' in sys.argv:
	print_timer = True

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

# Execute function
tweepy_pull(api, users, sell_coin, hold_time, volume, simulate, stream, wait_tweet=not skip_input, logfile=logfile, full_ex=full_ex, print_timer=print_timer, both=both, account_json=account_json_str[:-5])


