import ccxt
import time
from datetime import datetime
import json
import sys

# Executes buying and selling
class binance_api:

	# Initialize
	def __init__(self, api_keys, logfile=False):
		self.api_keys = {'api_key':api_keys['binance_keys']['api_key'],'secret_key':api_keys['binance_keys']['secret_key']}
		self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})
		self.logfile = logfile
	
	# Buying of real cryto
	def buy_crypto(self, ticker, buy_volume):
		
		# Try creating the buy order (10 times if doesn't go through)
		for i in range(10):
			try:
				buy_trade = self.exchange.create_order(ticker,'market','buy',buy_volume)
				print('\nBought')
				break
			except Exception as e:
				time.sleep(0.5)
				if i == 9:
					print('Exiting')
					exit()
				print(e)
				print('\nUnsucessful buy, trying again')
		
		# Print buy
		avg_price = sum([float(x['price']) * float(x['qty']) for x in buy_trade['info']['fills']])/sum([float(x['qty']) for x in buy_trade['info']['fills']])
		print('\nBought %s of %s at %s with %s %s of fees on %s' % (buy_trade['amount']\
			  , buy_trade['symbol'], avg_price, buy_trade['fee']['cost'], buy_trade['fee']['currency']\
			  , datetime.now().strftime('%b %d - %H:%M:%S')))

		return buy_trade

	# Selling of real crypto
	def sell_crypto(self, ticker, buy_volume, buy_trade):
		for i in range(100):
			try:				
				if buy_trade['fee']['currency'] == 'BNB':
				    sell_volume = buy_volume
				else:
				    # Converting fee currency to buy currency
				    ticker_pair = ticker.split('/')
				    if ticker_pair[0] != buy_trade['fee']['currency']:
				        fee_pair = [ticker_pair[0], buy_trade['fee']['currency']]
				        fee_ticker = '/'.join(fee_pair)
				        if fee_ticker not in tickers:
				            fee_ticker = '/'.join(fee_pair[::-1])
				        fee = self.exchange.fetchTicker(fee_ticker)
				        fee_price = (fee['bid'] + fee['ask']) /2
				        sell_volume = buy_volume - fee_price * buy_trade['fee']['cost']
				    
				    # When fee currency is the same as the buy currency
				    else:
				        sell_volume = buy_volume - buy_trade['fee']['cost']

				sell_trade = self.exchange.create_order(ticker,'market','sell',sell_volume)
				print('\nSold')
				break

			except Exception as e:
				error = e
				if 'MIN_NOTIONAL' in str(error):
					buy_volume = buy_volume *1.0005
				elif 'insufficient balance' in str(error):
					buy_volume = buy_volume * 0.9995
				else:
					self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})
				print(e)
				print('\n\nTrying to sell %.10f again' % buy_volume)
		
		# Print sell
		avg_price = sum([float(x['price']) * float(x['qty']) for x in sell_trade['info']['fills']])/sum([float(x['qty']) for x in sell_trade['info']['fills']])
		print('\nSold %s of %s at %s with %s %s of fees on %s' % (sell_trade['amount'], sell_trade['symbol'], avg_price\
			  , sell_trade['fee']['cost'], sell_trade['fee']['currency'], datetime.now().strftime('%b %d - %H:%M:%S')))

		return sell_trade

	# Get data from self.exchange and print it 
	def simulate_trade(self, buy, volume, ticker, conversion):
		if conversion[-4:] == 'USDT':
			usdpair = {'bid':1,'ask':1}
		else:
			usdpair = self.exchange.fetchTicker(conversion)
		if buy:
			bid_ask, buy_sell = 'ask', 'Buying'
		else:
			bid_ask, buy_sell = 'bid', 'Selling'
		try:
			trade_price = self.exchange.fetchTicker(ticker)[bid_ask]
			price = (usdpair['bid']+usdpair['ask'])/2
			print('\n{} {} at {:.8f} {} = {:.6f}$'.format(buy_sell, volume, trade_price, ticker, trade_price * volume * price))

		except Exception as e:
			print (e, '\nError in fetching ticker info')
		trade = {'symbol': ticker,'side':'buy' if buy else 'sell', 'amount':volume, 'cost':trade_price * volume}
		
		return trade


	# Summarise trade buy and sell
	def print_summary(self, simulate, ticker, buy_trade, sell_trade, conversion):
		
		if not simulate:
			buy_id, sell_id = buy_trade['info']['orderId'], sell_trade['info']['orderId']
			buy_prices, sell_prices = [], []
			for i in range(20):
				try:
					trades = self.exchange.fetchMyTrades(ticker,limit = 30)
				except Exception as e:
					print(e)
					print("Couldn't fetch trades, tying again")
					
			# Loop over trades as one order could have had multiple fills
			for trade in trades[::-1]:
			    if buy_id == trade['info']['orderId']:
			        buy_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']})
			    elif sell_id == trade['info']['orderId']:
			        sell_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']}) # Actual return uses fills
			buy_fee = sum([x['fee']['cost'] for x in buy_prices])
			sell_fee = sum([x['fee']['cost'] for x in sell_prices])        

			for i in range(20):
				try:
					if buy_trade['fee']['currency'] == 'BNB':
					    bnb_dollar = self.exchange.fetch_ticker('BNB/USDT')
					    bnb_price = (bnb_dollar['bid'] + bnb_dollar['ask']) / 2
					    buy_fee_dollar = buy_fee * bnb_price
					    if sell_trade['fee']['currency'] == 'BNB':
					        sell_fee_dollar = sell_fee * bnb_price
					else:
					    buy_crypto_dollar = self.exchange.fetch_ticker(buy_trade['fee']['currency']+'/USDT')
					    sell_crypto_dollar = self.exchange.fetch_ticker(sell_trade['fee']['currency']+'/USDT')
					    buy_fee_price = (buy_crypto_dollar['bid']+buy_crypto_dollar['ask'])/2
					    sell_fee_price = (sell_crypto_dollar['bid']+sell_crypto_dollar['ask'])/2
					    
					    buy_fee_dollar = buy_fee_price * buy_fee
					    sell_fee_dollar = sell_fee_price * sell_fee

					ticker_pair = ticker.split('/')
					if ticker_pair[1] == 'USDT':
						ticker_info = {'bid':1,'ask':1}
					else:
						ticker_info = self.exchange.fetch_ticker(ticker_pair[1]+'/'+'USDT')
				except Exception as e:
					print(e)
					print('Trying fetch again')
		else:
			sell_fee_dollar, buy_fee_dollar = 0, 0
			if ticker[-4:] == 'USDT':
				ticker_info = {'bid':1, 'ask':1}
			else:
				ticker_info = self.exchange.fetch_ticker(ticker.split('/')[1]+'/'+'USDT')

		print('\nGain/Loss: $%.6f' % ((sell_trade['cost'] - buy_trade['cost'])*(ticker_info['bid'] + ticker_info['ask'])\
		      / 2 - sell_fee_dollar - buy_fee_dollar))


	# Execute trade
	def execute_trade(self, pair, hold_time=60, buy_volume=50, simulate=False):

		# Ticker and convesion to USD strings for Kraken
		sell_volume = buy_volume
		ticker = pair[0]+'/'+pair[1]
		tousd1 = pair[0]+'/USDT'
		tousd2 = pair[1]+'/USDT'

		# Buy order
		if not simulate:
			buy_trade = self.buy_crypto(ticker, buy_volume)
		else:
			buy_trade = self.simulate_trade(True, buy_volume, ticker, tousd2)

		time.sleep(hold_time)

		# Sell order
		if not simulate:
			sell_trade = self.sell_crypto(ticker, buy_volume, buy_trade)
		else:
			sell_trade = self.simulate_trade(False, sell_volume, ticker, tousd2)

		# Summarize
		# if not simulate:
		self.print_summary(simulate, ticker, buy_trade, sell_trade, tousd2)
		if self.logfile:
			now = datetime.now().strftime("%y-%m-%d_%H:%M:%S")
			with open("prev_trades/trades_%s_binance_%s.txt" % (now,'simulation' if simulate else 'live'), "w") as log_name:
				json.dump({'time':now,'buy':buy_trade,'sell':sell_trade}, log_name)



