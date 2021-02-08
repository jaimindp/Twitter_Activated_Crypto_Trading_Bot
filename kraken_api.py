import krakenex
from pykrakenapi import KrakenAPI
import json
import requests
import pandas
import base64
# import ccxt


# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
kraken_keys = {'api_key':api_keys['krakenapi_keys']['api_key'],'secret_key':api_keys['krakenapi_keys']['secret_key']}


# api = krakenex.API()
api = krakenex.API(key=kraken_keys['api_key'], secret=kraken_keys['secret_key'])
k = KrakenAPI(api)
# ohlc, last = k.get_ohlc_data("DOGEUSD")
# print(ohlc)


# kraken = ccxt.kraken({'apiKey':kraken_keys['api_key'],'secret':kraken_keys['secret_key']})
# kraken.load_markets()
# kraken.create_order('BTC/USD', 'market', 'buy', 0.01, None, {'leverage': 3})




# print(k.get_open_orders())
# print(k.get_account_balance())
# print(k.get_trade_balance())


# header = {'API-Key' : kraken_keys['api_key'],'API-Sign':kraken_keys['api_key']}

# rest = 'https://futures.kraken.com/derivatives/api/v3'
# rest = 'https://futures.kraken.com/derivatives/api/v3/openorders'


