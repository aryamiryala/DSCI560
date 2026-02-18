import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self, initial_capital, transaction_cost=5.00):
        """
        transaction_cost: Flat fee per trade (e.g., $5.00)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.transaction_cost = transaction_cost
        self.holdings = {}  
        self.history = []   

    def run_backtest(self, price_df, signals_dict):
        """
        price_df: DataFrame with columns as tickers, index as dates
        signals_dict: Dictionary {ticker: signals_dataframe}
        """
        
        for ticker in price_df.columns:
            self.holdings[ticker] = 0

        # Loop through every day 
        for date in price_df.index:
            daily_value = self.cash
            
            for ticker in price_df.columns:
                current_price = price_df.loc[date, ticker]
                
                # Check if signal in this day
                if date in signals_dict[ticker].index:
                    signal = signals_dict[ticker].loc[date, 'positions']
                    
                    # BUY
                    if signal == 1.0:
                        if self.cash > current_price + self.transaction_cost:
                            shares_to_buy = (self.cash * 0.2) // current_price # Invest 20% of cash
                            if shares_to_buy > 0:
                                cost = (shares_to_buy * current_price) + self.transaction_cost
                                self.cash -= cost
                                self.holdings[ticker] += shares_to_buy
                                # print(f"BOUGHT {ticker} on {date}")

                    # SELL
                    elif signal == -1.0:
                        if self.holdings[ticker] > 0:
                            revenue = (self.holdings[ticker] * current_price) - self.transaction_cost
                            self.cash += revenue
                            self.holdings[ticker] = 0
                            # print(f"SOLD {ticker} on {date}")

                # Add stock value to daily total
                daily_value += self.holdings[ticker] * current_price

            self.history.append({'Date': date, 'Total Value': daily_value})

        return pd.DataFrame(self.history).set_index('Date')

def calculate_metrics(portfolio_history, initial_capital):
    final_val = portfolio_history['Total Value'].iloc[-1]
    total_return = (final_val - initial_capital) / initial_capital
    
    daily_returns = portfolio_history['Total Value'].pct_change().dropna()
    sharpe = np.sqrt(252) * (daily_returns.mean() / daily_returns.std())
    
    return total_return, sharpe, final_val