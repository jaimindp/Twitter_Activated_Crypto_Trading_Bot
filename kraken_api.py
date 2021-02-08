import json
import requests
import ccxt


# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()

kraken_keys = {'api_key':api_keys['krakenapi_keys']['api_key'],'secret_key':api_keys['krakenapi_keys']['secret_key']}
k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})
pair = 'DOGE/BTC'
# trade = k.create_order(pair,'market','buy',50)
