import time

# Gathers prices from exchange to trade against coin
class exchange_pull:

	def __init__(self, exchange, hold_times, base_coin = 'BTC'):
		self.exchange = exchange.exchange
		self.base_coin = base_coin
		self.stopflag = False
		self.count_pulls = 0
		self.hold_times = hold_times
		self.buy_sell_vols = {}

	# Retrieve tickers which have volume and trades against the base coin
	def get_tickers(self):
		
		# Fetch the tickers where there is volume for the trading pair agains the base coin
		try:
			self.all_tickers = self.exchange.fetch_tickers()
			self.markets = self.exchange.fetch_markets()

			volume_tickers = {k: v for k, v in self.all_tickers.items() if v['askVolume'] != 0 and v['bidVolume'] != 0}
			ticker_list = list(volume_tickers.keys())
			ticker_list = filter(lambda x : '/' in x, ticker_list)
			ticker_split = [i.split('/') for i in ticker_list]
			coin_tickers = ['/'.join(i) for i in list(filter(lambda x: self.base_coin == x[1], ticker_split))]
			self.cryptos  = set([i.split('/')[0] for i in coin_tickers])

			if self.count_pulls % 6 == 1:
				print('\nPulling live prices, there are %d crypto tickers you can trade on exchange against %s' % (len(self.cryptos), self.base_coin))
			
			# Get the BTC/USDT rate as well (approx)
			self.btc_usdt = self.all_tickers['BTC/USDT']['last']
			self.count_pulls += 1
		
		except Exception as e:
			print('\nError fetching tickers\n')
			print(e)


	# Start a cancellable loop of updating prices (usually as a thread)
	def buy_sell_volumes(self, buy_dollars, interval): # FIND OUT ABOUT LEVERAGED LIMITS AND SELL INCREMENTS

		while 1:
			if self.stopflag:
				return
			self.get_tickers()

			# Calulate buy and sell amounts
			btc_buy_amount = buy_dollars / self.btc_usdt
			
			# Loop over each crypto and calculate buy volume, then add to buy_sell_vols dict
			for coin in self.cryptos:
				symbol = coin + '/' + self.base_coin
				this_buy_vol = btc_buy_amount / self.all_tickers[symbol]['ask']
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

			time.sleep(interval)

