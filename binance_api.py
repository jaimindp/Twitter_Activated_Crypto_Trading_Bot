import json
import ccxt
import time


def execute_trade(keys, pair, hold_time=60, buy_volume=50, simulate=False):

	kraken_keys = {'api_key':keys['krakenapi_keys']['api_key'],'secret_key':keys['krakenapi_keys']['secret_key']}
	k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

	# Hardcode for now
	ticker = pair[0]+'/'+pair[1]
	tousd = pair[0]+'/USD'

	if not simulate:
		trade = k.create_order(ticker,'market','buy',buy_volume)
		
		print('\n',trade)
	
	usdpair = k.fetchTicker(tousd)
	print('\nBuying {} {} at {:.8f} which is ${:.8f}'.format(buy_volume,pair,k.fetchTicker(ticker)['bid'],(usdpair['bid']+usdpair['ask'])/2))

	time.sleep(hold_time)

	if not simulate:
		trade = k.create_order(ticker,'market','sell',buy_volume)
		print('\n',trade)
		
	usdpair = k.fetchTicker(tousd)
	print('\nSelling {} {} at {:.8f} which is ${:.8f}\n'.format(buy_volume,pair,k.fetchTicker(ticker)['ask'],(usdpair['bid']+usdpair['ask'])/2))

