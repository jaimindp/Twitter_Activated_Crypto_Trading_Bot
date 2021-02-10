# Tweet Activated Crypto Trader

### Feb 10th 2021 - uses either Kraken (US) or Binance (Non-US) tested on DOGE/BTC (Kraken & Binance), DOGT/GBP (Binance), made a 17% return from Elon's latest Doge tweet

The idea is to buy crypto using a Twitter trigger and sell after a user specified time / price / % gain e.g. when Elon musk tweets about Dogecoin

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, crypto pumps. We can capitalize on this opportunity by being one of the first to exectue trades when a tweet is posted

Currently looks for substring keyword matches in order to execute the trade

## To Do
- Backtest (done)
- User input parameters (done)
- Error handling if trade is unclosed (done)
- Fully implement Binance (lower taker/maker fees - 0.01% compared to Krakens 0.26%) (done)
- Trade logging json mechanism
- Reduce latency between tweet and trade from 3s to <1s
- Get a list of accounts to follow
- Test for multiple other cryptos/alt coins
- Mechanism for pulling out of all positions
- Limit orders
- Implement sentiment feature for size of position or whether to short (potentially object detection)


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt
	- Uses ccxt (cryptocurrency exchange trading library which has support for a huge number of exchanges and APIs)





