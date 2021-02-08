import json
import ccxt
import time


# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()

kraken_keys = {'api_key':api_keys['krakenapi_keys']['api_key'],'secret_key':api_keys['krakenapi_keys']['secret_key']}
k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})

# Hardcode for now
pair = 'DOGE/BTC'
tousd = 'DOGE/USD'
sleeptime = 2
buy_amount = 50

usdpair = k.fetchTicker(tousd)
print('Buying {} {} at {:.8f} which is ${:.5f} '.format(buy_amount,pair,k.fetchTicker(pair)['bid'],(usdpair['bid']+usdpair['ask'])/2))
# trade = k.create_order(pair,'market','buy',buy_amount)

time.sleep(sleeptime)
usdpair = k.fetchTicker(tousd)
print('Selling {} {} at {:.8f} which is ${:.5f} '.format(buy_amount,pair,k.fetchTicker(pair)['ask'],(usdpair['bid']+usdpair['ask'])/2))
# trade = k.create_order(pair,'market','sell',buy_amount)

