import ccxt
import time
from datetime import datetime
import json
import os
import sys

# Executes buying and selling
class kraken_api:

	# Initialize
	def __init__(self, api_keys, logfile=False):
		self.api_keys = {'api_key':api_keys['kraken_keys']['api_key'],'secret_key':api_keys['kraken_keys']['secret_key']}
		self.exchange = ccxt.kraken({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})
		self.logfile = logfile
	
	# Buying of real cryto
	def buy_crypto(self, ticker, buy_volume):
		
		# Try creating the buy order
		bought = False
		for _ in range(10):	
			try:
				buy_trade = self.exchange.create_order(ticker,'market','buy',buy_volume)
				print('\nBought')
				bought = True
				break
			except Exception as e:
				print(e)
				print('\nDid not buy correctly, trying again')

		print('\nBought %.8f at %s' % (buy_volume, datetime.now().strftime('%b %d - %H:%M:%S')))

		return buy_trade, buy_volume, bought

	# Selling of real crypto
	def sell_crypto(self, ticker, sell_volume):

		# Try to sell 10 times
		for i in range(10):
			try:
				sell_trade = self.exchange.create_order(ticker,'market','sell',sell_volume)
				print('\nSold')
				break

			except Exception as e:
				print(e)
				print('\n\nTrying to sell %.10f again' % buy_volume)
		
		# Print sell
		print('\nSold %.8f at %s' % (sell_volume, datetime.now().strftime('%b %d - %H:%M:%S')))

		return sell_trade

	# Get data from self.exchange and print it 
	def simulate_trade(self, buy, volume, ticker, conversion):
		if conversion[-4:] in ['USDT', 'USD']:
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
	def print_summary(self, simulate, ticker, buy_trade, sell_trades, conversion):
		
		if not simulate:
			buy_id, sell_ids = buy_trade['id'], [i['id'] for i in sell_trades]
			buy_prices, sell_prices = [], []
			for i in range(20):
				try:
					trades = self.exchange.fetch_my_trades(ticker)
					break
				except Exception as e:
					print(e)
					print("Couldn't fetch trades, tying again")
					
			# Loop over trades as one order could have had multiple fills
			for trade in trades[::-1]:
				if buy_id == trade['order']:
					buy_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']})
				elif trade['order'] in sell_ids:
					sell_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']}) # Actual return uses fills

			buy_fee = sum([x['fee']['cost'] for x in buy_prices])
			sell_fee = sum([x['fee']['cost'] for x in sell_prices])        

			# Log fees
			for i in range(20):
				try:
					if buy_prices[0]['fee']['currency'] in ['USDT', 'USD']:
						buy_fee_dollar = buy_fee
						sell_fee_dollar = sell_fee
					else:
						buy_crypto_dollar = self.exchange.fetch_ticker(buy_prices[0]['fee']['currency']+'/USDT')
						sell_crypto_dollar = self.exchange.fetch_ticker(sell_prices[0]['fee']['currency']+'/USDT')
						buy_fee_price = (buy_crypto_dollar['bid']+buy_crypto_dollar['ask'])/2
						sell_fee_price = (sell_crypto_dollar['bid']+sell_crypto_dollar['ask'])/2
						
						buy_fee_dollar = buy_fee_price * buy_fee
						sell_fee_dollar = sell_fee_price * sell_fee

					ticker_pair = ticker.split('/')
					if ticker_pair[1] in ['USDT', 'USD']:
						ticker_info = {'bid':1,'ask':1}
					else:
						ticker_info = self.exchange.fetch_ticker(ticker_pair[1]+'/'+'USDT')
				except Exception as e:
					print(e)
					print('\nError in printing executed trades')
		else:
			sell_prices, buy_prices = sell_trades, [buy_trade]
			sell_fee_dollar, buy_fee_dollar = 0, 0
			if ticker[-4:] in ['USDT', 'USD']:
				ticker_info = {'bid':1, 'ask':1}
			else:
				ticker_info = self.exchange.fetch_ticker(ticker.split('/')[1]+'/'+'USDT')

		print('\nGain/Loss: $%.6f' % ((sum([i['cost'] for i in sell_prices]) - sum(i['cost'] for i in buy_prices)) * (ticker_info['bid'] + ticker_info['ask'])\
			  / 2 - sell_fee_dollar - buy_fee_dollar))


	# Execute trade
	def execute_trade(self, pair, hold_time=60, buy_volume=50, simulate=False):

		# Ticker and convesion to USD strings for Kraken
		ticker = pair[0]+'/'+pair[1]
		tousd1 = pair[0]+'/USDT'
		tousd2 = pair[1]+'/USDT'

		# Buy order
		if not simulate:
			bought = False
			try:
				buy_trade, buy_volume, bought = self.buy_crypto(ticker, buy_volume)
			except Exception as e:
				print(e)
			if not bought:
				print('Exiting')
				exit()
		else:
			buy_trade = self.simulate_trade(True, buy_volume, ticker, tousd2)


		# Sell in multiple stages based on hold_time
		sell_volume = buy_volume / len(hold_time)
		prev_sell_time = 0
		sell_trades = []
		for hold in hold_time:
			time.sleep(hold - prev_sell_time)
			prev_sell_time = hold

			# Sell order
			if not simulate:
				sell_trades.append(self.sell_crypto(ticker, sell_volume))
			else:
				sell_trades.append(self.simulate_trade(False, sell_volume, ticker, tousd2))

		print('\n\nTRADING FINISHED\n')

		# Print summary 
		try:
			self.print_summary(simulate, ticker, buy_trade, sell_trades, tousd2)
		except Exception as e:
			print('\nFailed to print summary\n')
			print(e)

		# Log trade
		if self.logfile:
			now = datetime.now().strftime("%y-%m-%d_%H:%M:%S")
			if 'prev_trades' not in os.listdir():
				os.mkdir('prev_trades')
			with open("prev_trades/trades_%s_kraken_%s.txt" % (now,'simulation' if simulate else 'live'), "w") as log_name:
				json.dump({'time':now,'buy':buy_trade,'sell':sell_trades}, log_name)
