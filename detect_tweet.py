import tweepy
import json

# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}


# Test fastest way to detect tweet
elon = ['elonmusk',44196397]
me = ['ArbitrageDaddy', 1351770767130673152]


auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth)

tweets = api.user_timeline(screen_name=elon[0], 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = True,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )


print(tweets)


tweets2 = tw.Cursor(api.search,
              q=search_words,
              lang="en",
              since=date_since).items(5)


for tweet in tweets:
	print(tweet.text)

