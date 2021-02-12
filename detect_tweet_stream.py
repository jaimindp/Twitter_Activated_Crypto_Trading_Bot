# Another method using streaming (mitigates the wait on rate limit issue)
import tweepy
import time
import sys
import json
import inspect
import sys
from datetime import datetime
from tweepy import Stream
from tweepy.streaming import StreamListener

# Read keys
f = open('../twitter_keys2.json','r')
api_keys = json.loads(f.read())
f.close()

twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}

# Use twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
user = 'EDogeman'
user = '1359911287489236997'
keyword = 'hello'

# Old method of 1 per second
print('Method Get 1, or Stream 2')
method = input()

if method == '1':
	tweets = tweepy.Cursor(api.user_timeline, screen_name=user, include_rts=True, exclude_replies=True, tweet_mode="extended", count=1,wait_on_rate_limit=True,wait_on_rate_limit_notify=True).items(1)
	now = datetime.now()
	print(now)
	for new_tweet in tweets:
		print(new_tweet.full_text.lower())
else:
	class Listener(StreamListener):
		
		def __init__(self, output_file=sys.stdout):
			super(Listener,self).__init__()
			# self.output_file = output_file
		
		def on_status(self, status):
			now = datetime.now()
			print(now)
			print(status.text)
		
		def on_error(self, status_code):
			print(status_code)
			return False


	output = open('stream_output.txt', 'w')
	listener = Listener(output_file=output)

	stream = Stream(auth=api.auth, listener=listener)
	try:
		print('Start streaming.')
		# stream.sample(languages=['en'])
		stream.filter(follow=[user])

	except KeyboardInterrupt as e :
		print("Stopped.")
	finally:
		print('Done.')
		stream.disconnect()
		output.close()
