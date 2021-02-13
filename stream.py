# Another method using streaming (mitigates the wait on rate limit issue)
import tweepy
import time
import json
import sys
from datetime import datetime
from tweepy import Stream
from tweepy.streaming import StreamListener


# Listener class
class Listener(StreamListener):
	def __init__(self, ids, log_file=None):
		super(Listener,self).__init__()
		self.ids = ids
		self.log_file = log_file

	
	def on_status(self, status):
		# print('\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), status.text, status.user.screen_name, status.user.id_str))
		# print(status.user.id_str)
		# print(type(status.user.id_str),type(status.user.id_str))
		if str(status.user.id_str) in self.ids:
			print('\n\n\n%s: %s \n\n%s %s' % (datetime.now().strftime('%H:%M:%S'), status.text, status.user.screen_name, status.user.id_str))
			print(status.created_at)
			if any(word in status.text.lower() for word in keywords):
				print('\n\nFOUND AND READY TO BET\n\n')
				# Execute trade
				if self.log_file:
					self.log_file.write(status)
	
	def on_error(self, status_code):
		print(status_code)
		return False

# Stream tweets
def stream_tweets(api, users, id_set, keywords=None, log_file=None):
	
	listener = Listener(id_set, log_file=log_file)
	stream = Stream(auth=api.auth, listener=listener, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	try:
		print('Starting stream')
		stream.filter(follow=users, track=keywords)
		# stream.filter(follow=users, track=keywords, is_async=True)

	except KeyboardInterrupt as e:
		stream.disconnect()
		print("Stopped stream")
		exit()
	finally:
		print('Done')
		stream.disconnect()


# Read keys
f = open('../twitter_keys2.json','r')
api_keys = json.loads(f.read())
f.close()

twitter_keys = {'consumer_key':api_keys['twitter_keys']['consumer_key'],'consumer_secret':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['twitter_keys']['access_token_secret']}

# Use Twitter API
auth = tweepy.OAuthHandler(twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
auth.set_access_token(twitter_keys['access_token_key'], twitter_keys['access_token_secret'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Get users, ids must be in str format for stream
users = [['EDogeman',1359911287489236997], ['ArbitrageDaddy',1351770767130673152], ['elonmusk',44196397] ,['eToroUS', 1057583585715253248], ['eToro', 23420231], ['eTorox', 1027170867049111552], ['tyler', 24222556], ['Gemini', 2815661158], ['HuobiGlobal', 914029581610377217], ['Poloniex', 2288889440], ['OKEx', 867617849208037377], ['BinanceUS', 1115465940831891457], ['kucoincom', 910110294625492992], ['Bitstamp', 352518189], ['CoinbasePro', 720487892670410753], ['BithumbOfficial', 908496633196814337], ['bitfinex', 886832413], ['krakenfx', 1399148563], ['BittrexExchange', 2309637680], ['coinbase', 574032254], ['BTCTN', 3367334171], ['CoinDesk', 1333467482], ['binance', 877807935493033984], ['Bitcoin', 357312062], ['MKBHD', 29873662], ['CoinMarketCap', 2260491445], ['PeterLBrandt', 247857712], ['JoeBiden', 939091], ['POTUS', 1349149096909668363], ['JeffBezos', 15506669], ['tim_cook', 1636590253], ['sundarpichai', 14130366], ['satyanadella', 20571756], ['jack', 12], ['michael_saylor', 244647486], ['ToshiStreetBets', 1231601392139329536], ['CoinDeskMarkets', 956155022957531137], ['TrueCrypto28', 947954652770844672], ['FeraSY1', 951888527079497728], ['rektcapital', 918122676195090433], ['crypto_rand', 859484337850523648], ['Tradermayne', 2446024556], ['Rager', 2409661538], ['ThisIsNuse', 27583645], ['BigCheds', 129935623], ['BTC_JackSparrow', 380546370], ['filbfilb', 1036115996], ['cointradernik', 2372712211], ['PhilakoneCrypto', 715133222976270336], ['CryptoDonAlt', 878219545785372673], ['rogerkver', 176758255], ['SatoshiLite', 14338147], ['pmarca', 5943622], ['officialmcafee', 961445378], ['Raticoin1', 942966319229566977], ['TheRoaringKitty', 2902349190], ['VitalikButerin', 295218901], ['LucidMotors', 487094283], ['Rivian', 260414018], ['ARKInvest', 2398137084], ['ParikPatelCFA', 1295526279194828800], ['ArbitrageBoiUK', 1239432784319406080], ['tegmark', 2530947115], ['SureBetz', 1338951559732994049], ['CathieDWood', 2361631088], ['RaoulGMI', 2453385626], ['chamath', 3291691], ['virgingalactic', 26208862], ['Ripple', 1051053836], ['binancescalping', 1083619608433704962], ['MikeyFourTweets', 1275300939646156802], ['StockMKTNewz', 1250830691824283648], ['EfforceOfficial', 1006922925541412864]]
user_ids = list(map(lambda x:str(x[1]), users))
id_set = set(user_ids)  

# Keywords to look for
keywords = ['btc', 'coin', 'bitcoin', 'breakout']
keyword_set = set(keywords)

# Set up logging
log_file = None
if 'l' in sys.argv:
	log_file = open('stream_output.txt', 'a')

# Stream tweets 
while 1:
	try:
		stream_tweets(api, user_ids, id_set, keywords, log_file)
	except Exception as e:
		print(e)
	

# stream_tweets(api, user_ids, id_set)



