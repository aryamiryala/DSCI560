import pandas as pd
import data_loader
import strategies
import backtester
import matplotlib.pyplot as plt

def main():
    
    tickers = ['AAPL', 'NVDA', 'TSLA'] # multiple stocks
    start_date = "2024-01-01"
    end_date = "2026-02-04"
    initial_capital = 100000.0
    trans_cost = 5.0 # transacation fee


    print("--- Loading Data ---")
    prices_df = data_loader.fetch_data(tickers, start_date, end_date)
    print(prices_df.head())

   
    print("\n--- Generating Signals ---")
    
   
    sma_signals = {}
    hybrid_signals = {}
    arima_signals = {}
    lstm_signals = {}
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        stock_prices = prices_df[ticker].dropna()
        
        # sma
        sma_signals[ticker] = strategies.generate_sma_signals(stock_prices)
        
        # hybrid
        hybrid_signals[ticker] = strategies.generate_hybrid_signals(stock_prices)

        # arima
        arima_signals[ticker] = strategies.generate_arima_signals(stock_prices)
        
        # lstm
        print(f"  Training LSTM for {ticker}...")
        lstm_signals[ticker] = strategies.run_lstm_strategy(stock_prices)
        
    
    # backtest
    print("\n--- Running Backtest (SMA Portfolio) ---")
    portfolio_sma = backtester.Portfolio(initial_capital, transaction_cost=trans_cost)
    results_sma = portfolio_sma.run_backtest(prices_df, sma_signals)
    
    print("\n--- Running Backtest (Hybrid Portfolio) ---")
    portfolio_hybrid = backtester.Portfolio(initial_capital, transaction_cost=trans_cost)
    results_hybrid = portfolio_hybrid.run_backtest(prices_df, hybrid_signals)

    print("\n--- Running Backtest (ARIMA Portfolio) ---")
    portfolio_arima = backtester.Portfolio(initial_capital, transaction_cost=trans_cost)
    results_arima = portfolio_arima.run_backtest(prices_df, arima_signals)

    print("\n--- Running Backtest (LSTM Portfolio) ---")
    portfolio_lstm = backtester.Portfolio(initial_capital, transaction_cost=trans_cost)
    results_lstm = portfolio_lstm.run_backtest(prices_df, lstm_signals)

    # Calculate Metrics
    ret_sma, sharpe_sma, val_sma = backtester.calculate_metrics(results_sma, initial_capital)
    ret_hyb, sharpe_hyb, val_hyb = backtester.calculate_metrics(results_hybrid, initial_capital)
    ret_ari, sharpe_ari, val_ari = backtester.calculate_metrics(results_arima, initial_capital)
    ret_lst, sharpe_lst, val_lst = backtester.calculate_metrics(results_lstm, initial_capital)

    print("\n" + "="*30)
    print(f"FINAL RESULTS (Initial: ${initial_capital:,.2f})")
    print("="*30)
    print(f"SMA Strategy:")
    print(f"  Final Value: ${val_sma:,.2f}")
    print(f"  Return: {ret_sma:.2%}")
    print(f"  Sharpe Ratio: {sharpe_sma:.2f}")
    print("-" * 20)
    print(f"Hybrid Strategy:")
    print(f"  Final Value: ${val_hyb:,.2f}")
    print(f"  Return: {ret_hyb:.2%}")
    print(f"  Sharpe Ratio: {sharpe_hyb:.2f}")
    print("-" * 20)
    print(f"ARIMA Strategy:")
    print(f"  Final Value: ${val_ari:,.2f}")
    print(f"  Return: {ret_ari:.2%}")
    print(f"  Sharpe Ratio: {sharpe_ari:.2f}")
    print("-" * 20)
    print(f"LSTM Strategy:")
    print(f"  Final Value: ${val_lst:,.2f}")
    print(f"  Return: {ret_lst:.2%}")
    print(f"  Sharpe Ratio: {sharpe_lst:.2f}")
    
    plt.figure(figsize=(12,7))
    plt.plot(results_sma.index, results_sma['Total Value'], label='SMA Portfolio')
    plt.plot(results_hybrid.index, results_hybrid['Total Value'], label='Hybrid Portfolio')
    plt.plot(results_arima.index, results_arima['Total Value'], label='ARIMA Portfolio', linestyle='--')
    plt.plot(results_lstm.index, results_lstm['Total Value'], label='LSTM Portfolio', linestyle='-.')
    
    plt.title(f"Portfolio Performance (Transaction Cost: ${trans_cost})")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()