# Tweet Activated Crypto Trader

## Updates
### June 2nd 2021 - This project is now <a href='https://www.lazytrade.io'>www.lazytrade.io</a>. You can execute Twitter based crypto buying and selling through the Telegram messaging app!

March 23rd 2021 - Stopped updating repo, building functionality privately. Message for info.

twitter_exchanges.py works with querying. Issue with streaming fixed too. (Mar 23rd)

New thread created for trade so multiple trades can occur concurrently under streaming. Ctrl-c will allow the trades to close out in the given time and the program to exit automatically. (March 17th)

Fixed issue with querying. New coin listings from coinbase, coinbasepro and binance successfully traded +25%. Works when BNB is in binance account to take fees. (March 15th)

Buy amount now requested in $ and dynamically adjusted to valid crypto amount based on latest exchange rate. (Mar 9th)

Set up for futures trading up to 100x leverage (not on github), successfully returned 100%+ from Elon's doge tweets

## Overview
The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin or when a new coin is listed on an exchange

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency AKA crypto pumps. We can capitalise on this opportunity by being one of the first to exectue trades when a tweet is posted

As soon as Tweet is posted, ~5s with streaming/~1s querying, the program checks for substring matches with keywords for a particular cryptocurrency. These keywords and coins can be user specified from the keywords json files to implement any trade strategies

Threading for streaming tweets so trade executions run in a separate thread allowing multiple trades to occur at once. When ctrl-c is hit, it waits for the trades to sell automatically according to the specification then closes the program

The buy amount is input in $ and based on the latest prices from the exchange, the program  will calculate valid buy and (multiple) sell amounts as close to the specified $ amount as the market will allow (Binance). BNB coin required in account to take fees. With Kraken, the buy amount has to be a valid tradeable amount in crypto and when divided by the number of selling trades, also has to leave valid tradeable amounts 

To configure on local system: \
`pip install -r requirements.txt`

To run with Binance (monitors a single ticker): \
`python twitter_binance.py`

To run with Kraken (monitors a single ticker): \
`python twitter_kraken.py`

API keys are kept in a json, one directory up from repo ../keys.json
```
{
    "twitter_keys":{
        "consumer_key":"XXXXXXXXXXXXXXXXXXXX",
        "consumer_secret":"XXXXXXXXXXXXXXXXXXXX",
        "access_token_key":"XXXXXXXXXXXXXXXXXXXX",
        "access_token_secret":"XXXXXXXXXXXXXXXXXXXX"
    },
    "binance_keys":{
        "api_key":"XXXXXXXXXXXXXXXXXXXX",
        "secret_key":"XXXXXXXXXXXXXXXXXXXX"
    },
    "kraken_keys":{
    	"api_key":"XXXXXXXXXXXXXXXXXXXX",
        "secret_key":"XXXXXXXXXXXXXXXXXXXX"
    }
}
```
## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt (cryptocurrency exchange trading library)
	- ccxt allows universal function calls to be used on multiple exchanges (adding a new exchange should not be difficult as long as ccxt has the same functions implemented)
- If anything is not working correctly, let me know!
