import json
import requests
import ccxt


# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()

kraken_keys = {'api_key':api_keys['krakenapi_keys']['api_key'],'secret_key':api_keys['krakenapi_keys']['secret_key']}
pair = 'DOGEBTC'
buy_vol = '50'
buy_price = '0.000001'
ref_buy = 'jaimin1'

k = ccxt.kraken({'apiKey':kraken_keys['api_key'], 'secret':kraken_keys['secret_key']})
pair = 'XDGXBT'
k.create_order('DOGE/BTC','market','buy',50)
