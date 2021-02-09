# Tweet Activated Crypto Trader

# Feb 9th 2021 - can use either Kraken (US) or Binance (Non-US) and has been tested on DOGE/BTC

The idea is to buy crypto using a trigger e.g. when Elon musk tweets about Dogecoin and sell after a user specified time / price / % gain

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, essentially crypto pump and dumps. We can capitalize on this opportunity by being one of the first to exectue trades when listening for the information on social media

Currently looks for substring keyword matches in order to execute the trade

## To Do
- Backtest (done)
- User input parameters (done)
- Error handling if trade is unclosed (done)
- Fully implement Binance (lower taker/maker fees - 0.01% compared to Krakens 0.26%) (done)
- Trade logging json mechanism
- Get a list of accounts to follow
- Test for multiple other cryptos and alt coins
- Mechanism for pulling out of all positions
- Limit orders
- Implement sentiment feature for size of position or whether to short (potentially object detection)


## Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Requires a crypto exchange (Kraken/Binance) API which is used through ccxt
	- Uses ccxt (cryptocurrency exchange trading library which has support for a huge number of exchanges and APIs)





