# Tweet Activated Crypto Trader

### Feb 11th 2021 - has been tested on DOGE/BTC (Kraken & Binance), DOGE/GBP, BTC/GBP (Binance), successfully made a 17% & 3% return from Elon's latest Doge tweets

The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, crypto pumps. We can capitalize on this opportunity by being one of the first to exectue trades when a tweet is posted

When a Tweet is posted, it checks for substring matches with keywords for a particularcryptpcurrency, these keywords can be edited and more cryptos can be added in order to execute the trade

To configure on local system: 
`pip install -r requirements.txt`

To run with Binance: 
`python twitter_binance.py`

To run with Kraken: 
`python kraken_binance.py` 

API keys are kept in a json called one directory up from repo ../keys.json

## To Do
- Backtest (done)
- User input parameters (done)
- Error handling if trade is unclosed (done)
- Fully implement Binance (lower taker/maker fees - 0.01% compared to Krakens 0.26%) (done)
- Trade logging json mechanism
- Verify working on BTC
- Reduce latency between tweet and trade from 2s to < 1s 
	- Look at streaming twitter rather than querying every second
- Get a list of accounts to follow and trade ideas
- Retweets vs. Tweets
- Test for multiple other cryptos/alt coins
	- Test when ticker symbols are reversed
- Implement for any alt coin if listed on an exchange
- Mechanism for pulling out of all positions
- Limit orders
	- Trailing stop losses
- Implement sentiment feature
	- For size of position 
	- Shorting 
- Look at interpreting images (CV for text extraction, object detection on memes) 


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt
	- Uses ccxt (cryptocurrency exchange trading library which has support for a huge number of exchanges and APIs)





