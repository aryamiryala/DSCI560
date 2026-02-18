import yfinance as yf
import pandas as pd

def fetch_data(tickers, start_date, end_date):
    """
    Fetches daily Close prices for a list of tickers.
    Returns a DataFrame where columns are ticker names.
    """
    print(f"Downloading data for: {tickers}...")
    data = yf.download(tickers, start=start_date, end=end_date, interval="1d")
    
    # Handle MultiIndex if downloading multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        return data['Close']
    else:
        # If single ticker, ensure it returns a DataFrame with the ticker as column name
        df = data[['Close']].copy()
        df.columns = tickers
        return df