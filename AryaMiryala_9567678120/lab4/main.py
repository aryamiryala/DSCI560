# run all of the files and do evaluation metrics. print the results
#metrics: total return, annual return, ratio
from load import load_data
from alg import mov_avg_alg
from simulator import trading_sim
import numpy as np

def main():
    file_path = "somefileweget.csv"
    stock_data = load_data(file_path)
    prices = stock_data['Close']

    #can edit this parameteres for strat
    short_win = 10
    long_win = 30
    initial_cap = 10000
    risk_free_rate = 0.0

    signal = mov_avg_alg(prices, short_win, long_win)
    
    #run the simulator
    portfolio_values, daily_returns = trading_sim(prices, signal, initial_cap)

    #metrics

    # Total Return
    total_return = (portfolio_values[-1] - initial_cap) / initial_cap

    # Annualized Return (assuming 252 trading days)
    num_days = len(daily_returns)
    annualized_return = (1 + total_return) ** (252 / num_days) - 1

    # Sharpe Ratio - How much return you’re getting for each unit of risk you take
    avg_daily_return = np.mean(daily_returns)
    std_daily_return = np.std(daily_returns)

    if std_daily_return != 0:
        sharpe_ratio = (avg_daily_return - risk_free_rate) / std_daily_return
    else:
        sharpe_ratio = 0

    print("Final Portfolio Value:", portfolio_values[-1])
    print("Total Return:", total_return)
    print("Annualized Return:", annualized_return)
    print("Sharpe Ratio:", sharpe_ratio)


if __name__ == "__main__":
    main()