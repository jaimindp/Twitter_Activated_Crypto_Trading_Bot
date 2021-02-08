import tweepy
import json
import time


# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}


# Test fastest way to detect tweet
elon = ['elonmusk',44196397]
me = ['ArbitrageDaddy', 1351770767130673152]

user = me

lookfor = ['doge','crypto','dogecoin','coin']

auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

tweets = api.user_timeline(screen_name=user[0], 
                           # 200 is the maximum allowed count
                           count=2,
                           include_rts = True,
                           # Necessary to keep full_text
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )

for tweet in tweets:
	last_tweet = tweet
	break

new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], tweet_mode="extended", count=1).items(1))[0]

while new_tweet.full_text == last_tweet.full_text:
	new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], tweet_mode="extended", count=1).items(1))[0]
	time.sleep(0.1)

if any(i in new_tweet.full_text.lower() for i in lookfor):
	print('ola we going baby to the mooooooooon')



## Another method

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