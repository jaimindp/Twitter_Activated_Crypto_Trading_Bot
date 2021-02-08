import json
import ccxt
import time


def execute_trade(keys, hold_time=60, buy_volume=50, paper=False):

	kraken_keys = {'api_key':keys['krakenapi_keys']['api_key'],'secret_key':keys['krakenapi_keys']['secret_key']}
	k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

	# Hardcode for now
	pair = 'DOGE/BTC'
	tousd = 'DOGE/USD'

	if paper:
		usdpair = k.fetchTicker(tousd)
		print('Buying {} {} at {:.8f} which is ${:.5f} '.format(buy_volume,pair,k.fetchTicker(pair)['bid'],(usdpair['bid']+usdpair['ask'])/2))
	else:
		trade = k.create_order(pair,'market','buy',buy_volume)
		print(trade)

	time.sleep(hold_time)

	if paper:
		usdpair = k.fetchTicker(tousd)
		print('Selling {} {} at {:.8f} which is ${:.5f} '.format(buy_volume,pair,k.fetchTicker(pair)['ask'],(usdpair['bid']+usdpair['ask'])/2))
	else:
		trade = k.create_order(pair,'market','sell',buy_volume)
		print(trade)

