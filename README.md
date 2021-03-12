# Tweet Activated Crypto Trader

## Updates
### March 12th 2021 - New coin listings from coinbase, coinbasepro and binance successfully traded +25%. 

Buy amount now requested in $ and dynamically adjusted to valid crypto amount based on latest exchange rate. (Mar 9th)

Do not use query method as Twitter API not consistently returning correct results (Feb 24th)

Set up for futures trading up to 100x leverage (not on github), successfully returned 100%+ from Elon's doge tweets

Verified on DOGE/BTC (Kraken & Binance), DOGE/GBP, BTC/GBP (Binance), DOGE/USDT (Binance Futures), successfully made a 17%, 3%, 7% from DOGE/GBP spot trades

## Overview
The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin or when a new coin is listed on an exchange

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency AKA crypto pumps. We can capitalise on this opportunity by being one of the first to exectue trades when a tweet is posted

As soon as Tweet is posted, ~5s with streaming/~1s querying, the program checks for substring matches with keywords for a particular cryptocurrency. These keywords and coins can be user specified from the keywords json files to implement any trade strategies

The buy amount is input in $ and based on the latest prices from the exchange, the program  will calculate valid buy and (multiple) sell amounts as close to the specified $ amount as the market will allow (Binance). With Kraken the, buy amount has to be a valid tradeable amount and has to be divisible by the number of selling times

To configure on local system: \
`pip install -r requirements.txt`

To run with Binance (monitors a single ticker): \
`python twitter_binance.py`

New coin listings (Trades any pair listed on Binance): \
`python twitter_exchanges.py`

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

## To Do List
- Reduce latency between tweet and trade to 2s (done)
	- Use 1 query/s maximum from Twitter keys
	- Fix overloading queries issue
	- Look at streaming Twitter, streams can get multiple users rather than just 1 every second (slower ~ 5s)
		- Integrate streaming (done)
		- Allow monitoring of multiple accounts through streaming (done)
		- Prevent multiple trades of the same coin within a time window
- Implement futures trading to leverage larger sums of money (Not on github, message me)
	- USD(S)(Stablecoin pegged) currently USDT (Done)
- Subtract time it takes to run code from intervals
- Test for trading any alt coins (done)
	- For a previously untraded coin (done binance)
	- Handle multiple coins in the same tweet
		- Execute trade on coin with the lowest market cap
		- Execute trade on all coins at the same time
	- Dynamically adjust amounts to buy from prices with valid coin rounding (done)
	- Dynamically addjust amounts to valid % of coin wallet
	- Update exchange rates with one thread pulling prices and one thread checking for tweets (done)
	- Selling step size consideration so combined sales == buy (done)
	- Check leverage limits for coins
- Implement more sell options
	- Specified % gain
	- Limit order at a price target
	- Limit downside with a % drop cap to pull out of trade
	- Trailing stop losses (Can use ccxt for this)
	- Sell in chunks over user specified time (done)
	- Allow different hold times for different users and keywords
- Reduce fees using BNB coin and check working for all trades (done)
- Trade notification system
	- Slack API
	- Telegram API
- Machine Learning features
	- Sentiment feature
		- For size of position 
		- Shorting
	- Interpreting images (CV for text extraction, object detection on memes)


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt (cryptocurrency exchange trading library)
	- ccxt allows universal function calls to be used on multiple exchanges (adding a new exchange should not be difficult as long as ccxt has the same functions implemented)

