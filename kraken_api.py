import krakenex
from pykrakenapi import KrakenAPI
api = krakenex.API()
k = KrakenAPI(api)
ohlc, last = k.get_ohlc_data("BCHUSD")
print(ohlc)
