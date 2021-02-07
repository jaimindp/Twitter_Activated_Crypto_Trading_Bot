import krakenex
from pykrakenapi import KrakenAPI
import json

# Read keys
f = open('../keys.json','r')
api_keys = json.loads(f.read())
f.close()
kraken_keys = {'api_key':api_keys['krakenapi_keys']['api_key'],'secret_key':api_keys['twitter_keys']['consumer_secret'],'access_token_key':api_keys['twitter_keys']['access_token_key'],'access_token_secret': api_keys['krakenapi_keys']['secret_key']}

print(kraken_keys)


api = krakenex.API()
k = KrakenAPI(api)
ohlc, last = k.get_ohlc_data("BCHUSD")
print(ohlc)






