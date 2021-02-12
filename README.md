# Tweet Activated Crypto Trader

### Feb 11th 2021 - has been tested on DOGE/BTC (Kraken & Binance), DOGE/GBP, BTC/GBP (Binance), successfully made a 17% & 3% return from Elon's latest Doge tweets

The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, crypto pumps. We can capitalize on this opportunity by being one of the first to exectue trades when a tweet is posted

When a Tweet is posted, it checks for substring matches with keywords for a particular cryptocurrency

These keywords and coins can be user specified

To configure on local system: \
`pip install -r requirements.txt`

To run with Binance: \
`python twitter_binance.py`

To run with Kraken: \
`python kraken_api.py` 

API keys are kept in a json called one directory up from repo ../keys.json

## To Do
- Backtest (done)
- User input parameters (done)
- Error handling if trade is unclosed (done)
- Fully implement Binance (lower taker/maker fees - 0.01% compared to Krakens 0.26%) (done)
- Trade logging json mechanism (done)
- Verify working using BTC transactions (done)
- Reduce latency between tweet and trade from 2s to < 1s 
	- Look at streaming Twitter rather than querying every second
	- Selenium scraper
	- Requests module
- Get a list of accounts to follow and trade ideas
- Handle Retweets vs. Tweets
- Transfer list of keywords to text file
- Test for multiple other alt coins
	- Test when ticker symbols are reversed
- Work out the miniumum amounts for each alt
	- Find a reasonable amount to trade based of or previous exchange rates
- Implement for any alt coin if listed on an exchange
- Mechanism for pulling out of all positions
- Implement sell options
	- Specified % gain
	- Limit order at a price target
	- Trailing stop losses
- Machine Learning features
	- Implement sentiment feature
		- For size of position 
		- Shorting 
	- Look at interpreting images (CV for text extraction, object detection on memes) 


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt
	- Uses ccxt (cryptocurrency exchange trading library which has support for a huge number of exchanges and APIs)





