import ccxt
import time
from datetime import datetime
import json
import os
import sys

# Executes buying and selling
class binance_api:

	# Initialize
	def __init__(self, api_keys, logfile=False, block=False, account_json=None):
		self.api_keys = {'api_key':api_keys['binance_keys']['api_key'],'secret_key':api_keys['binance_keys']['secret_key']}
		self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})
		self.logfile = logfile
		self.block = block
		self.started_time = datetime.now()
		self.account_json = account_json

		# Set of tickers to block if specified
		if self.block:
			self.block_set = set()

	# Reset the exchange
	def refresh_exchange(self):
		self.exchange = ccxt.binance({'apiKey':self.api_keys['api_key'], 'secret':self.api_keys['secret_key']})

	# Buying of real cryto
	def buy_crypto(self, ticker, buy_volume):
		
		# Try creating the buy order
		for i in range(10):
			try:
				buy_trade = self.exchange.create_order(ticker,'market','buy',buy_volume)
				break
			except Exception as e:
				print(e)
				if i == 9:
					print('Could not buy, exiting thread')
					exit()
				print('\nBuy did not work, trying again')

		# Print buy
		try:
			if buy_trade.get('status') != 'open':
				avg_price = sum([float(x['price']) * float(x['qty']) for x in buy_trade['info']['fills']])/sum([float(x['qty']) for x in buy_trade['info']['fills']])
				print('\nBought %s of %s at %s with %s %s of fees on %s\n' % (buy_trade['amount']\
					  , buy_trade['symbol'], avg_price, buy_trade['fee']['cost'], buy_trade['fee']['currency']\
					  , datetime.now().strftime('%b %d - %H:%M:%S')))
			else:
				print('\nBought %.8f at %s\n' % (buy_volume, datetime.now().strftime('%b %d - %H:%M:%S')))
		except Exception as e:
			print(e)
			print('\nError in print of buy')

		return buy_trade, buy_volume

	# Selling of real crypto
	def sell_crypto(self, ticker, buy_volume, buy_trade):

		# Try to sell 10 times
		for i in range(10):
			try:
				# Fees in USDT, Buy/Sell crypto amount is equal -- check if behaviour is the same when you have BNB in the wallet
				if ticker[-4:] == 'USDT':
					sell_volume = buy_volume
				# If fees in the returned trade (filled on order)
				elif buy_trade['fee']:
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
				else:
					sell_volume = buy_volume

				sell_trade = self.exchange.create_order(ticker,'market','sell',sell_volume)
				break

			except Exception as e:
				error = e
				if 'MIN_NOTIONAL' in str(error):
					buy_volume = buy_volume *1.0005
				elif 'insufficient balance' in str(error):
					buy_volume = buy_volume * 0.9995
				else:
					self.refresh_exchange()
				print(e)
				print('\n\nTrying to sell %.10f again' % buy_volume)
		
		# Print sell
		if sell_trade['status'] != 'open':
			avg_price = sum([float(x['price']) * float(x['qty']) for x in sell_trade['info']['fills']])/sum([float(x['qty']) for x in sell_trade['info']['fills']])
			print('\nSold %s of %s at %s with %s %s of fees on %s' % (sell_trade['amount'], sell_trade['symbol'], avg_price\
				  , sell_trade['fee']['cost'], sell_trade['fee']['currency'], datetime.now().strftime('%b %d - %H:%M:%S')))
		else:
			print('\nSold %.8f at %s' % (sell_volume, datetime.now().strftime('%b %d - %H:%M:%S')))

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
			print('\n{} {} at {:.8f} {} = ${:.6f}'.format(buy_sell, volume, trade_price, ticker, trade_price * volume * price))

		except Exception as e:
			print (e, '\nError in fetching ticker info')
		trade = {'symbol': ticker,'side':'buy' if buy else 'sell', 'amount':volume, 'cost':trade_price * volume}
		
		return trade


	# Summarise trade buy and sell
	def print_summary(self, simulate, ticker, buy_trade, sell_trades, conversion):
		
		if not simulate:
			buy_id, sell_ids = buy_trade['info']['orderId'], [i['info']['orderId'] for i in sell_trades]
			buy_prices, sell_prices = [], []
			for i in range(20):
				try:
					trades = self.exchange.fetchMyTrades(ticker)
					break
				except Exception as e:
					print(e)
					print("Couldn't fetch trades, tying again")
					
			# Loop over trades as one order could have had multiple fills
			for trade in trades[::-1]:
				if buy_id == trade['info']['orderId']:
					buy_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']})
				elif trade['info']['orderId'] in sell_ids:
					sell_prices.append({'amount':trade['amount'],'cost':trade['cost'],'fee':trade['fee']}) # Actual return uses fills

			buy_fee = sum([x['fee']['cost'] for x in buy_prices])
			sell_fee = sum([x['fee']['cost'] for x in sell_prices])        

			# Log fees
			for i in range(20):
				try:
					if buy_prices[0]['fee']['currency'] == 'BNB':
						bnb_dollar = self.exchange.fetch_ticker('BNB/USDT')
						bnb_price = (bnb_dollar['bid'] + bnb_dollar['ask']) / 2
						buy_fee_dollar = buy_fee * bnb_price
						if sell_prices[0]['fee']['currency'] == 'BNB':
							sell_fee_dollar = sell_fee * bnb_price
					elif buy_prices[0]['fee']['currency'] == 'USDT':
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
					if ticker_pair[1] == 'USDT':
						ticker_info = {'bid':1,'ask':1}
					else:
						ticker_info = self.exchange.fetch_ticker(ticker_pair[1]+'/'+'USDT')
				except Exception as e:
					print(e)
					print('\nError in printing executed trades')
		else:
			sell_prices, buy_prices = sell_trades, [buy_trade]
			sell_fee_dollar, buy_fee_dollar = 0, 0
			if ticker[-4:] == 'USDT':
				ticker_info = {'bid':1, 'ask':1}
			else:
				ticker_info = self.exchange.fetch_ticker(ticker.split('/')[1]+'/'+'USDT')

		buy_total = sum(i['cost'] for i in buy_prices)
		sell_total = sum([i['cost'] for i in sell_prices])
		avg_bid_ask = (ticker_info['bid'] + ticker_info['ask']) / 2

		gain_loss = (sell_total - buy_total) * avg_bid_ask - sell_fee_dollar - buy_fee_dollar
		gain_loss_percent = gain_loss / (buy_total * avg_bid_ask - sell_fee_dollar - buy_fee_dollar) * 100

		gain_text = '\nProfit/Loss: $%.6f   %.3f%%' % (gain_loss, gain_loss_percent)
		print(gain_text)

		return gain_text, buy_total, sell_total

	# Send a telegram of the profits and losses
	def send_telegram(self, ticker, buy_total, sell_total, gain_text, status, simulate):
		
		# Sending a telegram message to myself
		import telegram
		with open('../telegram_keys.json') as json_file:
			telegram_dict = json.load(json_file)
			if type(status) == dict:
				full_info_text = '(%s) %s\nBought %.6f and sold %.6f BTC\n\n@%s - %s:\n"%s"\n' % (ticker, gain_text, float(buy_total), \
					float(sell_total), status['url'], status['update_time'].strftime('%m/%d %H:%M:%S'), status['update_text'])
			else:
				try:
					full_text = status.text
				except:
					full_text = status.full_text
				full_info_text = '(%s) %s\nBought %.6f and sold %.6f BTC\n\n@%s - %s:\n"%s"\n' % (ticker, gain_text, float(buy_total), \
					float(sell_total), status.user.screen_name, status.created_at.strftime('%m/%d %H:%M:%S'), full_text)
			
			bot = telegram.Bot(token=telegram_dict['api_key'])
			bot.send_message(chat_id=telegram_dict['chat_id'], text=full_info_text)


	# Log the trade
	def log_trade(self, ticker, buy_volume, hold_times, buy_trade, sell_trades, gain_text, status, simulate):
		# Log trade
		if self.logfile:
			now = datetime.now().strftime("%y-%m-%d_%H:%M:%S")

			# Saving name format: time_started, json_file_used, simluation/live
			with open("prev_trades/trades_%s_binance_%s_%s.txt" % (self.started_time.strftime('%Y-%m-%d_%H-%M-%S'), self.account_json, 'simulation' if simulate else 'live'), "a") as log_name:
				# If status is a dict, the message was from a web scrape
				if type(status) == dict:
					json.dump({'url':status['url'],'update_text':status['update_text'],'update_time':status['update_time'].strftime('%Y-%m-%d_%H:%M:%S'),'ticker':ticker,'hold_times':hold_times,'complete_time':now,'buy_volume':buy_volume,'buy':buy_trade,'sell':sell_trades,'telegram':gain_text}, log_name)	

				# If tweet from stream or query
				else:
					try:
						full_text = status.text
					except:
						full_text = status.full_text
					json.dump({'user':status.user.screen_name,'tweet':full_text,'tweet_time':status.created_at.strftime('%Y-%m-%d_%H:%M:%S'),'ticker':ticker,'hold_times':hold_times,'complete_time':now,'buy_volume':buy_volume,'buy':buy_trade,'sell':sell_trades,'telegram':gain_text}, log_name)
				log_name.write('\n')


	# Execute trade
	def execute_trade(self, pair, hold_times=60, buy_volume=50, simulate=False, status=None):

		# Dealing with buy_sell volume pair or just a buy_volume
		if type(buy_volume) != list:
			sell_volumes = [buy_volume / len(hold_times) for _ in hold_times]
		else:
			sell_volumes = buy_volume[1]
			buy_volume = buy_volume[0]

		# Ticker and convesion 
		ticker = pair[0]+'/'+pair[1]
		tousd1 = pair[0]+'/USDT'
		tousd2 = pair[1]+'/USDT'

		# If there is a block put on trading this ticker
		if self.block:
			if ticker in self.block_set:
				print('\nTrade of ' + ticker + ' blocked in ' + str(self.block_set))
				return

		# Buy order
		if not simulate:
			buy_trade, buy_volume = self.buy_crypto(ticker, buy_volume)
		else:
			buy_trade = self.simulate_trade(True, buy_volume, ticker, tousd2)
		
		# When bought add and blocker flag set
		if self.block:
			self.block_set.add(ticker)

			print('Added to blockset '+str(self.block_set))

		# Sell in multiple stages based on hold_times
		prev_sell_time = 0
		sell_trades = []
		for hold, sell_volume in zip(hold_times, sell_volumes):
			time.sleep(hold - prev_sell_time)
			prev_sell_time = hold

			# Sell order
			if not simulate:
				sell_trades.append(self.sell_crypto(ticker, sell_volume, buy_trade))
			else:
				sell_trades.append(self.simulate_trade(False, sell_volume, ticker, tousd2))

		# Remove block when trade finishes
		if self.block:
			self.block_set.remove(ticker)
			print('Removing %s from block set' % (ticker))

		print('\n\nTRADE FINISHED\n')

		# Print summary and log
		try:
			gain_text, buy_total, sell_total = self.print_summary(simulate, ticker, buy_trade, sell_trades, tousd2)
		except Exception as e:
			print('\nFailed to print summary\n')
			print(e)

		# Send telegram message
		if 'telegram_keys.json' in os.listdir('../'): #and not self.simulate:
			self.send_telegram(ticker, buy_total, sell_total, gain_text, status, simulate)

		# Log trade
		if self.logfile:
			self.log_trade(ticker, buy_volume, hold_times, buy_trade, sell_trades, gain_text, status, simulate)
			