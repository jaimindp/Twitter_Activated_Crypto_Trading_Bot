# Tweet Activated Crypto Trader

### Feb 26th 2021 - Twitter query API overloaded on Elon's twitter timeline and behaving incorrectly. Switchng code to streaming tweets rather than querying tweets. Set up for futures trading (not on github) which can use leverage up to 20x. Successfully returned 120% (DOGE/USDT Perpetual) from Elon's latest doge tweet. 

Verified on DOGE/BTC (Kraken & Binance), DOGE/GBP, BTC/GBP (Binance), DOGE/USDT (Binance Futures), successfully made a 17%, 3%, 7% from DOGE/GBP spot trades

The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, crypto pumps. We can capitalize on this opportunity by being one of the first to exectue trades when a tweet is posted

When a Tweet is posted, it checks for substring matches with keywords for a particular cryptocurrency

These keywords and coins can be user specified

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
- User input parameters (done)
- Error handling if trade is unclosed (done)
- Fully implement Binance (lower taker/maker fees < 0.1% compared to Krakens 0.26%) (done)
- Trade logging json mechanism (done)
- Verify working using BTC transactions (done)
- Reduce latency between tweet and trade to 2s (done)
	- Use 1 query/s maximum from Twitter keys
	- Fix overloading queiries issue
	- Look at streaming Twitter, streams can get multiple users rather than just 1 every second (slower ~ 5s)
		- Integrate streaming (done)
		- Allow monitoring of multiple accounts through streaming
	- Selenium scraper (slow)
	- Requests package (doesn't work with Twitter)
- Get a list of accounts to follow and trade ideas
- Implement futures trading to leverage larger sums of money (Not on github)
	- USD(S)(Stablecoin pegged) currently USDT (Done)
	- Coin(m) crypto pegged BTC or ETH
- Handle Retweets vs. Tweets
- Subtract time it takes to run code from intervals
- Create keyword list in json file (done)
	- Keyword confidences = position size
- Test for multiple other alt coins
- Test when ticker symbols are reversed
	- For a previously untraded coin
- Work out the amount to buy for each alt
	- Find a reasonable amount to trade based of previous exchange rates in £/$
	- Keep a list of exchange rates in memory or in text file and update a a certain freq / at the start
- Implement for any previously untraded alt coin if listed on Binance or Kraken
- Implement more sell options
	- Specified % gain
	- Limit order at a price target
	- Trailing stop losses (Can use ccxt for this)
	- Sell in chunks over user specified time (done)
- Reduce fees using BNB coin and check working for all trades
- Machine Learning features
	- Sentiment feature
		- For size of position 
		- Shorting
	- Interpreting images (CV for text extraction, object detection on memes)


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt (cryptocurrency exchange trading library)
	- ccxt allows universal function calls to be used on multiple exchanges (adding a new exchange should not be difficult)

