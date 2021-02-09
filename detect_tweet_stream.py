import tweepy
import json
import time
from kraken_api import *

# Checks if a tweet from a user contains a particular trigger word
def tweepy_pull(api, user, pair, crypto, hold_time, volume, simulate):
	print(pair)
	while 1:
		tweets = api.user_timeline(user_id=user[1], 
		                           count=1,
		                           include_rts = True,
		                           tweet_mode = 'extended',
		                           wait_on_rate_limit=True,
		                           wait_on_rate_limit_notify=True
		                           )

		for tweet in tweets:
			last_tweet = tweet
			break

		new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], tweet_mode="extended", count=1).items(1))[0]

		while new_tweet.full_text == last_tweet.full_text:
			new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], tweet_mode="extended", count=1).items(1))[0]
			time.sleep(1)

		if any(i in new_tweet.full_text.lower() for i in crypto['triggers']):
			execute_trade(api_keys, pair, hold_time=hold_time, buy_volume=volume, simulate=simulate)
			print('ola we going baby to the mooooooooon!\n\n')

# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}


# User and crypto selection
users ={'elon':['elonmusk',44196397], 'me':['ArbitrageDaddy', 1351770767130673152]} 
cryptos = {'dogecoin':{'triggers':['doge',' ','hodl','doggo'],'symbol':'DOGE'}, 'bitcoin':{'triggers':['bitcoin', 'btc',' crypto', 'buttcoin'],'symbol':'BTC'},'usd':{'symbol':'USD'}}

# Get user inputs
print('\nEnter crypto to buy: '+'%s '* len(cryptos) % tuple(cryptos.keys()))
skip_input = False
crypto  = input()
if not crypto:
	crypto = 'dogecoin'
	skip_input = True
buy_coin = cryptos[crypto]

if not skip_input:
	print('\nEnter currency to sell: '+'%s '* len(cryptos) % tuple(cryptos.keys()))
	sell_coin  = cryptos[input()]
else:
	sell_coin = cryptos['bitcoin']

pair = [buy_coin['symbol'],sell_coin['symbol']]

if not skip_input:
	print('\nUser: '+'%s '* len(users) % tuple(users.keys())) 
	username = input()
	user = users[username]
else:
	user = users['me']

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


if not skip_input:
	print('\nVolume in crypto: ')
	volume = input()
	if not volume:
		if crypto == 'dogecoin':
			volume = 50
		elif crypto == 'bitcoin':
			volume = 0.0002
	else:
		volume = float(volume)
else:
	volume = 50
print('\nVolume %.8f %s' % (volume, buy_coin['symbol']))

if not skip_input:
	print('\nTest y/n:')
	test = input()
	simulate = True
	if test == 'n': simulate = False
else:
	simulate = True

print('\nWaiting to match a tweet\n')

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

# Execute function
tweepy_pull(api, user, pair, buy_coin, hold_time, volume, simulate)

## Another method using streaming (mitigates the wait on rate limit issue)

# import tweepy
# import time
# import sys
# import inspect

# consumer_key = 'xxxxxxxxxxxxxxxxxxx'
# consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# access_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# access_token_secret = 'xxxxxxxxxxxxxxxx'

# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
# auth.secure = True

# api = tweepy.API(auth)

# class MyStreamListener(tweepy.StreamListener):
#     def on_status(self, status):
#             if  status.user.screen_name.encode('UTF-8').lower() == 'someuser':
#                 print 'TWEET:', status.text.encode('UTF-8')
#                 print 'FOLLOWERS:', status.user.followers_count
#                 print time.ctime()
#                 print '\n'

# myStreamListener = MyStreamListener()
# myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener())
# myStream.filter(follow=['someuserid'])