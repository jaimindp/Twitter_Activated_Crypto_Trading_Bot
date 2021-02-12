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
user = ['EDogeman', '1359911287489236997']
user2 = ['ArbitrageDaddy', '1351770767130673152']

users = [784732198758916096,
	 1360116716198498304,
	 1162479826546151424,
	 30050590,
	 1114541814760050689,
	 1359907509306351616,
	 1321845532353044480,
	 1160508244491567105,
	 1360116635735003136,
	 1360112177214984192,
	 1357608757178507267,
	 1358906969973743620,
	 1360118276827713538,
	 1171056581770977280,
	 1360118305244209153,
	 1236644542276931586,
	 1360116391253270532,
	 4816454868,
	 1360116158062600192,
	 1206809839034343425,
	 1836191161,
	 2780473738,
	 2909235422,
	 1360116239121543172,
	 637016855,
	 232520602,
	 1360118372680142850,
	 1360115604913590273,
	 1360114737443266563,
	 1360117738434228224,
	 1360115449061470210,
	 1180349500986216449,
	 3430317432,
	 1360117121385181187,
	 715865037190086656,
	 1304877269874343937,
	 1106570383111516162,
	 15285381,
	 1360116021936414720,
	 106079073,
	 1360118071692730369,
	 1360112129542619141,
	 1360117969062305794,
	 1360118402732482563,
	 1360117420971622400,
	 1359771442091601921,
	 1262224544380514304,
	 4340721616,
	 1355181695247421440,
	 1360117642900561920,
	 1360117663406690305,
	 748301778853175296,
	 794200957882081280,
	 1047934159614889984,
	 1360117321914851337,
	 1360118312378728448,
	 1357374951272181761,
	 983599019296468992,
	 1099689360054734849,
	 1354668458143789060,
	 1212852239867318272,
	 40706406,
	 1360118231437082624,
	 1360117473824051201,
	 3092865720,
	 1360117729429082116,
	 1360118079137677312,
	 1248008969911562241,
	 1360117459391418368,
	 1169348347540451328,
	 1829864016,
	 1360117854897459201,
	 1360117893728530434,
	 1221545630549651457,
	 548820758,
	 49467377,
	 1360117823343783936,
	 105970060,
	 1360116277847740419,
	 887701618417860609,
	 1360072320102985731,
	 1360118239125241858,
	 1360108974305996803,
	 2929716995,
	 770893631700041728,
	 2894775969,
	 2999122211,
	 1360118419014758400,
	 160923123,
	 873092399433523200,
	 1357686402629029893,
	 1233799524218327040,
	 1150540646,
	 1346739765824147457,
	 1360117763881263106,
	 769806525997129728,
	 272365752,
	 1183370873283084288,
	 1360118251124973570,
	 1360116536283779072]

users = [str(i) for i in users]

keyword = 'hello'

# Old method of 1 per second
print('Method Get 1, or Stream 2')
method = input()

if method == '1':
	while 1:
		tweets = api.user_timeline(user_id=user[1], 
			                           count=1,
			                           include_rts = True,
			                           exclude_replies = True,
			                           tweet_mode = 'extended',
			                           wait_on_rate_limit=True,
			                           wait_on_rate_limit_notify=True
			                           )

		last_tweet = new_tweet = tweets[0]
		print('\nWaiting for {} to tweet\n'.format(user[0]))

		while new_tweet.full_text == last_tweet.full_text:
			try:
				new_tweet = list(tweepy.Cursor(api.user_timeline, user_id=user[1], include_rts=True, exclude_replies=True, tweet_mode="extended", count=1,wait_on_rate_limit=True, wait_on_rate_limit_notify=True).items(1))[0]	
			except Exception as e:
				print(e,'\nFailed at tweet collector\n')
			time.sleep(1)

		now = datetime.now()
		print(now)
		for new_tweet in tweets:
			print(new_tweet.full_text)
else:
	class Listener(StreamListener):
		
		def __init__(self, output_file=sys.stdout):
			super(Listener,self).__init__()
		
		def on_status(self, status):
			now = datetime.now()
			print(now)
			print(status.text)
		
		def on_error(self, status_code):
			print(status_code)
			return False


	output = open('stream_output.txt', 'w')
	listener = Listener(output_file=output)

	stream = Stream(auth=api.auth, listener=listener, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
	try:
		print('Start streaming.')
		stream.filter(follow=users)
		# stream.filter(follow=[user[1], user2[1]], is_async=True)
		# stream.filter(follow=[user[1], user2[1]], is_async=True)
		print('hi')

	except KeyboardInterrupt as e :
		print("Stopped.")
	finally:
		print('Done.')
		stream.disconnect()
		output.close()
