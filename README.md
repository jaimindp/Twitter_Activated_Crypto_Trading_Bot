# Tweet Activated Crypto Trader

### March 5th 2021 - Switched code to streaming tweets rather than querying tweets due to API errors. Set up for futures trading (not on github) which can use leverage up to 20x. Successfully returned 120%, 50%, 40% (DOGE/USDT Perpetual) from Elon's latest doge tweets. 

Verified on DOGE/BTC (Kraken & Binance), DOGE/GBP, BTC/GBP (Binance), DOGE/USDT (Binance Futures), successfully made a 17%, 3%, 7% from DOGE/GBP spot trades

The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, crypto pumps. We can capitalize on this opportunity by being one of the first to exectue trades when a tweet is posted

When a Tweet is posted, it checks for substring matches with keywords for a particular cryptocurrency. These keywords and coins can be user specified

The buy amount must be input in valid tradeable crypto units and this number must be divisible by the number of sell trades (valid in tradeable crypto units)

To configure on local system: \
`pip install -r requirements.txt`

To run with Binance: \
`python twitter_binance.py`

To run with Kraken: \
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

## To Do
- Reduce latency between tweet and trade to 2s (done)
	- Use 1 query/s maximum from Twitter keys
	- Fix overloading queries issue
	- Look at streaming Twitter, streams can get multiple users rather than just 1 every second (slower ~ 5s)
		- Integrate streaming (done)
		- Allow monitoring of multiple accounts through streaming (done)
- Implement futures trading to leverage larger sums of money (Not on github, message me)
	- USD(S)(Stablecoin pegged) currently USDT (Done)
	- Coin(m) crypto pegged BTC or ETH
- Subtract time it takes to run code from intervals
- Keywords and confidences
	- Handle multiple coins in the same tweet
- Test for trading any alt coins (done)
	- For a previously untraded coin (done binance)
- Work out the amount to buy for each alt
	- Fix pulling error in list threaded daemon
	- Find a reasonable amount to trade based of previous exchange rates in £/$ (done)
	- Keep a list of exchange rates in memory with one thread as stream thread checks for tweets (done)
	- Selling step size consideration
- Implement more sell options
	- Specified % gain
	- Limit order at a price target
	- Trailing stop losses (Can use ccxt for this)
	- Sell in chunks over user specified time (done)
- Reduce fees using BNB coin and check working for all trades
	- Spot (done)
	- Futures
- Take out mention param for streaming and use user id instead (done)
- Machine Learning features
	- Sentiment feature
		- For size of position 
		- Shorting
	- Interpreting images (CV for text extraction, object detection on memes)


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt (cryptocurrency exchange trading library)
	- ccxt allows universal function calls to be used on multiple exchanges (adding a new exchange should not be difficult)

