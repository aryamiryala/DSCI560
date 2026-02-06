import pandas as pd
import numpy as np


#use LSTM to forecast prices, then apply a moving-average-based rule to 
# turn those forecasts into trading signals.

#calculates the moving average from price data
def moving_avg(price, window):
    prices = pd.Series(prices)
    return prices.rolling(window=window).mean()

#decision logic. Buy, Sell, or hold
def mov_avg_alg(prices, short_window, long_window):
    #1-buy, -1 sell, 0- hold
    prices = pd.Series(prices)

    short_ma = moving_avg(prices, short_window)
    long_ma = moving_avg(prices, long_window)

    signals = pd.Series(0, index=prices.index)

    for i in range(1, len(prices)):
        # Buy signal: short MA crosses above long MA
        if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
            signals[i] = 1

        # Sell signal: short MA crosses below long MA
        elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
            signals[i] = -1

        # Otherwise: Hold
        else:
            signals[i] = 0

    return signals


