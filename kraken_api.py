import json
import ccxt
import time

# Executes buying and selling
def execute_trade(keys, pair, hold_time=60, buy_volume=50, simulate=False):

	kraken_keys = {'api_key':keys['krakenapi_keys']['api_key'],'secret_key':keys['krakenapi_keys']['secret_key']}
	k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

	# Ticker and convesion to USD strings for Kraken
	ticker = pair[0]+'/'+pair[1]
	tousd1 = pair[0]+'/USD'
	tousd2 = pair[1]+'/USD'

	# Try creating they buy order 10 times
	if not simulate:
		for i in range(10):
			try:
				trade = k.create_order(ticker,'market','buy',buy_volume)
				break
			except:
				if i == 9:
					print('Exiting')
					exit()
				print('Unsucessful buy, trying again')
		print('\n',trade)
	try:
		usdpair1 = k.fetchTicker(tousd1)
		bid = k.fetchTicker(ticker)['bid']
		price = (usdpair1['bid']+usdpair1['ask'])/2
		print('\nBuying {} at {:.8f} {} = {:.6f}$'.format(buy_volume, bid, ticker, buy_volume*price))
	
	except Exception as e:
		print(e, '\nerror in some fetch of info')

	time.sleep(hold_time)

	# Sell order
	if not simulate:
		for i in range(10000):
			try:
				trade = k.create_order(ticker,'market','sell',buy_volume)
				break
			except Exception as e:
				print(e, '\n\ntrying to sell position again')
				k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})
		print('\n',trade)

	usdpair1 = k.fetchTicker(tousd1)
	ask = k.fetchTicker(ticker)['ask']
	price = (usdpair1['bid']+usdpair1['ask'])/2
	print('\nSelling {} at {:.8f} {} = {:.6f}$\n'.format(buy_volume, ask, ticker,  buy_volume*price))

	if not simulate:
		trades = k.fetchMyTrades(ticker)
		usdpair2 = k.fetchTicker(tousd2)
		sell = trades[-1]
		buy = trades[-2]
		print('\nGain/Loss: ${:.6f}:\n'.format((sell['cost']-buy['cost']-buy['fee']['cost']-sell['fee']['cost'])*(usdpair2['bid']+usdpair2['ask'])/2))


