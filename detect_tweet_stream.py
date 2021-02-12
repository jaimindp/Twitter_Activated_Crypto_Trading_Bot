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

users = [['eToroUS', 1057583585715253248], ['eToro', 23420231], ['eTorox', 1027170867049111552], ['tyler', 24222556], ['Gemini', 2815661158], ['HuobiGlobal', 914029581610377217], ['Poloniex', 2288889440], ['OKEx', 867617849208037377], ['BinanceUS', 1115465940831891457], ['kucoincom', 910110294625492992], ['Bitstamp', 352518189], ['CoinbasePro', 720487892670410753], ['BithumbOfficial', 908496633196814337], ['bitfinex', 886832413], ['krakenfx', 1399148563], ['BittrexExchange', 2309637680], ['coinbase', 574032254], ['BTCTN', 3367334171], ['CoinDesk', 1333467482], ['binance', 877807935493033984], ['Bitcoin', 357312062], ['MKBHD', 29873662], ['CoinMarketCap', 2260491445], ['PeterLBrandt', 247857712], ['JoeBiden', 939091], ['POTUS', 1349149096909668363], ['JeffBezos', 15506669], ['tim_cook', 1636590253], ['sundarpichai', 14130366], ['satyanadella', 20571756], ['jack', 12], ['michael_saylor', 244647486], ['ToshiStreetBets', 1231601392139329536], ['CoinDeskMarkets', 956155022957531137], ['TrueCrypto28', 947954652770844672], ['FeraSY1', 951888527079497728], ['rektcapital', 918122676195090433], ['crypto_rand', 859484337850523648], ['Tradermayne', 2446024556], ['Rager', 2409661538], ['ThisIsNuse', 27583645], ['BigCheds', 129935623], ['BTC_JackSparrow', 380546370], ['filbfilb', 1036115996], ['cointradernik', 2372712211], ['PhilakoneCrypto', 715133222976270336], ['CryptoDonAlt', 878219545785372673], ['rogerkver', 176758255], ['SatoshiLite', 14338147], ['pmarca', 5943622], ['officialmcafee', 961445378], ['Raticoin1', 942966319229566977], ['TheRoaringKitty', 2902349190], ['VitalikButerin', 295218901], ['LucidMotors', 487094283], ['Rivian', 260414018], ['ARKInvest', 2398137084], ['ParikPatelCFA', 1295526279194828800], ['ArbitrageBoiUK', 1239432784319406080], ['tegmark', 2530947115], ['SureBetz', 1338951559732994049], ['CathieDWood', 2361631088], ['RaoulGMI', 2453385626], ['chamath', 3291691], ['virgingalactic', 26208862], ['Ripple', 1051053836], ['binancescalping', 1083619608433704962], ['MikeyFourTweets', 1275300939646156802], ['StockMKTNewz', 1250830691824283648], ['EfforceOfficial', 1006922925541412864]]


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
