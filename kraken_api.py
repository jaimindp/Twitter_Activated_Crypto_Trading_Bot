import json
import ccxt
import time


def execute_trade(keys, pair, hold_time=60, buy_volume=50, simulate=False):

	kraken_keys = {'api_key':keys['krakenapi_keys']['api_key'],'secret_key':keys['krakenapi_keys']['secret_key']}
	k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

	# Hardcode for now
	ticker = pair[0]+'/'+pair[1]
	tousd1 = pair[0]+'/USD'
	tousd2 = pair[1]+'/USD'

	if not simulate:
		trade = k.create_order(ticker,'market','buy',buy_volume)
		print('\n',trade)
	
	usdpair1 = k.fetchTicker(tousd1)
	bid = k.fetchTicker(ticker)['bid']
	price = (usdpair1['bid']+usdpair1['ask'])/2
	print('\nBuying {} at {:.8f} {} = {:.6f}$'.format(buy_volume, bid, ticker, buy_volume*price))

	time.sleep(hold_time)

	if not simulate:
		trade = k.create_order(ticker,'market','sell',buy_volume)
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


