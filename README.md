# tweet_activated_crypto_trader

(Feb 8th 2021 - work in progress, uses Kraken exchange for buying Dogecoin in the US)

The idea is to buy crypto using a trigger e.g. when Elon musk tweets about Dogecoin and sell after a user specified time / price / % gain

Markets, particularly small market cap altcoins are heavily influenced by individuals with large following 'hyping' up a cryptocurrency, essentially crypto pump and dumps. We can capitalize on this opportunity by being one of the first to exectue trades when listening for the information on social media

Currently looks for substring keyword matches in order to execute the trade

To Do
- Backtest
- User input parameters
- Implement sentiment feature
- Object detection in images

Notes
- Requires a Twitter Developer API detecting tweets through Tweepy
- Uses ccxt (cryptocurrency exchange trading library which has support for a huge number of exchanges and APIs)




