import ccxt
import time

# Executes buying and selling
class binance_api:

	def __init__(self, api_keys):
		self.api_keys = {'api_key':api_keys['binance_keys']['api_key'],'secret_key':api_keys['binance_keys']['secret_key']}
		self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})


	# Buying of real cryto
	def buy_crypto(self, ticker, buy_volume):
		# Try creating the buy order (10 times if doesn't go through)
		for i in range(10):
			try:
				buy_trade = self.exchange.create_order(ticker,'market','buy',buy_volume)
				break
			except:
				time.sleep(0.5)
				if i == 9:
					print('Exiting')
					exit()
				print('Unsucessful buy, trying again')
		print('\n',buy_trade)
		return buy_trade

	# Selling of real crypto
	def sell_crypto(self, ticker, sell_volume):
		for i in range(10000):
			try:
				sell_trade = self.exchange.create_order(ticker,'market','sell',sell_volume)
				break
			except Exception as e:
				print(e, '\n\nTrying to sell position again')
			self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})
		print('\n',sell_trade)

		return sell_trade

	# Get data from self.exchange and print it 
	def print_price(self, buy, volume, ticker, conversion):
		try:
			usdpair = self.exchange.fetchTicker(conversion)
		except:
			usdpair = self.exchange.fetchTicker(conversion+'T')
		if buy == True:
			bid_ask, buy_sell = 'bid', 'Buying'
		else:
			bid_ask, buy_sell = 'ask', 'Selling'
		try:
			symbol_info = self.exchange.fetchTicker(ticker)[bid_ask]
			price = (usdpair['bid']+usdpair['ask'])/2
			print('\n{} {} at {:.8f} {} = {:.6f}$'.format(buy_sell, volume, symbol_info, ticker, volume*price))

		except Exception as e:
			print (e, '\nError in fetching ticker info')

	# Summarize trade buy and sell
	def print_summary(self, ticker, buy_trade, sell_trade, conversion):
		buy, sell = None, None
		for trade in self.exchange.fetchMyTrades(ticker,limit=6)[::-1]:
			if trade['info']['orderId'] == buy_trade['info']['orderId']:
				buy = trade
			elif trade['info']['orderId'] == sell_trade['info']['orderId']:
				sell = trade
			if buy is not None and sell is not None:
				try:
					usd_sell = self.exchange.fetchTicker(sell['fee']['currency']+'/USD')
					usd_buy = self.exchange.fetchTicker(buy['fee']['currency']+'/USD')
					usdpair = self.exchange.fetchTicker(conversion)
				except:
					usd_sell = self.exchange.fetchTicker(sell['fee']['currency']+'/USDT')
					usd_buy = self.exchange.fetchTicker(buy['fee']['currency']+'/USDT')
					usdpair = self.exchange.fetchTicker(conversion+'T')
				print('\nGain/Loss: ${:.6f}:\n'.format((sell['cost']-buy['cost'])*(usdpair['bid']+usdpair['ask'])/2\
				       									-buy['fee']['cost']*usd_buy['bid']\
				       									-sell['fee']['cost']*usd_sell['bid']))
				break


	# Execute trade
	def execute_trade(self, pair, hold_time=60, buy_volume=50, simulate=False):

		# Ticker and convesion to USD strings for Kraken
		sell_volume = buy_volume
		ticker = pair[0]+'/'+pair[1]
		tousd1 = pair[0]+'/USD'
		tousd2 = pair[1]+'/USD'

		# Buy order
		if not simulate:
			buy_trade = self.buy_crypto(ticker, buy_volume)
		self.print_price(True, buy_volume, ticker, tousd1)

		time.sleep(hold_time)

		# Sell order
		if not simulate:
			sell_volume = buy_volume - buy_trade['fee']['cost']
			sell_trade = self.sell_crypto(ticker, sell_volume)
		self.print_price(False, sell_volume, ticker, tousd1)

		# Summarize
		if not simulate:
			self.print_summary(ticker, buy_trade, sell_trade, tousd2)


