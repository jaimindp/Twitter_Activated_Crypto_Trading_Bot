import time
import traceback
import ccxt
from  datetime import datetime

# Gathers prices from exchange to trade against coin
class exchange_pull:

	def __init__(self, exchange, hold_times, base_coin='BTC', coin_subset=None):
		self.exchange = exchange.exchange
		self.my_exchange = exchange
		self.base_coin = base_coin
		self.stopflag = False
		self.count_pulls = 0
		self.hold_times = hold_times
		self.coin_subset = coin_subset
		self.buy_sell_vols = {}


	# Retrieve tickers which have volume and trades against the base coin
	def get_tickers(self):
		
		# Fetch the tickers where there is volume for the trading pair agains the base coin
		try:
			# Using a subset of tickers from coin_subset
			if self.coin_subset:
				self.all_tickers, self.markets = {}, {}
				for coin_pair in self.coin_subset:
					coin_pair += '/'+self.base_coin
					self.all_tickers[coin_pair] = self.exchange.fetch_ticker(coin_pair)
					self.markets = list(filter(lambda x : x['id'] == coin_pair.replace('/',''), self.exchange.fetch_markets()))

				# Add exchange rate with base coin and USDT
				if self.base_coin != 'USDT':
					try:
						self.all_tickers[self.base_coin+'/USDT'] = self.exchange.fetch_ticker(self.base_coin+'/USDT')
					except Exception as e:
						print(e)
			
			# Using all tickers
			else:
				self.all_tickers = self.exchange.fetch_tickers()
				self.markets = self.exchange.fetch_markets()

			volume_tickers = {k: v for k, v in self.all_tickers.items() if v['askVolume'] != 0 and v['bidVolume'] != 0}
			ticker_list = list(volume_tickers.keys())
			ticker_list = filter(lambda x : '/' in x, ticker_list)
			ticker_split = [i.split('/') for i in ticker_list]
			coin_tickers = ['/'.join(i) for i in list(filter(lambda x: self.base_coin == x[1], ticker_split))]
			self.cryptos  = set([i.split('/')[0] for i in coin_tickers])

			
			# Get the COIN/USDT rate as well (approx)
			if self.base_coin == 'USDT':
				self.all_tickers['USDT/USDT'] = {}
				self.all_tickers['USDT/USDT']['last'] = 1
				self.all_tickers['USDT/USDT']['ask'] = 1
			
			self.coin_usdt = self.all_tickers[self.base_coin+'/USDT']['last']

		except Exception as e:
			print('\nError fetching tickers, check buy and sell coins have pair on exchange\n')
			# print(traceback.format_exc())
			print(e)


	# Start a cancellable loop of updating prices (usually as a thread)
	def buy_sell_volumes(self, buy_dollars, interval): # FIND OUT ABOUT LEVERAGED LIMITS AND SELL INCREMENTS

		while 1:

			# Refresh the whole exchange so new tickers are included not just new prices		
			if self.count_pulls % 10 == 0 and self.coin_subset is None:
				print('\nExchange refreshed')
				self.my_exchange.refresh_exchange()

			# Set as cancellable thread on wakeup
			if self.stopflag:
				return

			self.get_tickers()

			# Calulate buy and sell amounts
			buy_amount = buy_dollars / self.coin_usdt
			
			# Loop over each crypto and calculate buy volume, then add to buy_sell_vols dict
			for coin in self.cryptos:
				symbol = coin + '/' + self.base_coin
				if self.all_tickers[symbol]['ask'] == None:
					this_buy_vol = buy_amount / float(self.all_tickers[symbol]['info']['lastPrice'])
				else:
					this_buy_vol = buy_amount / self.all_tickers[symbol]['ask']
				
				# Get market relevant for this coin
				market = list(filter(lambda x : x['id'] == symbol.replace('/',''), self.markets))
				if market:
					step_size = float(market[0]['info']['filters'][2]['stepSize'])
					buy_vol_rounded = round(this_buy_vol * 1/step_size) * step_size
					
					# Calcluate sell amounts
					sell_cumulative = 0
					sell_vol = round((this_buy_vol/ len(self.hold_times)) * 1/step_size) * step_size
					sell_vols_rounded = []

					# Set all sell volumes to a correct size
					for i in range(len(self.hold_times)-1):
						sell_cumulative += sell_vol
						sell_vols_rounded.append(sell_vol)

					# Last sell volume is the excess to make it exactly equal to the buy volume
					sell_vols_rounded.append(round((buy_vol_rounded - sell_cumulative) * 1/step_size) * step_size)
					self.buy_sell_vols[coin] = [buy_vol_rounded, sell_vols_rounded]
			
			# Print 1 in 10 updates
			if self.count_pulls % 10 == 0:
				print('Pulled live prices (updates every 20 mins), there are %d tradeable tickers with %s - %s' % (len(self.cryptos), self.base_coin, datetime.now().strftime('%m/%d - %H:%M:%S')))
			
			self.count_pulls += 1
			time.sleep(interval)

