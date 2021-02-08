import json
import ccxt
import time


def execute_trade(keys, pair, hold_time=60, buy_volume=50, simulate=False):

	kraken_keys = {'api_key':keys['krakenapi_keys']['api_key'],'secret_key':keys['krakenapi_keys']['secret_key']}
	k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

	# Hardcode for now
	ticker = pair[0]+'/'+pair[1]
	tousd = pair[0]+'/USD'

	if simulate:
		usdpair = k.fetchTicker(tousd)
		print('Buying {} {} at {:.8f} which is ${:.8f} '.format(buy_volume,pair,k.fetchTicker(ticker)['bid'],(usdpair['bid']+usdpair['ask'])/2))
	else:
		trade = k.create_order(ticker,'market','buy',buy_volume)
		print(trade)

	time.sleep(hold_time)

	if simulate:
		usdpair = k.fetchTicker(tousd)
		print('\nSelling {} {} at {:.8f} which is ${:.8f} '.format(buy_volume,pair,k.fetchTicker(ticker)['ask'],(usdpair['bid']+usdpair['ask'])/2))
	else:
		trade = k.create_order(ticker,'market','sell',buy_volume)
		print(trade)

