import pandas as pd

def load_data(file):
    stock_data = pd.read_csv(file)
    stock_data['Date']= pd.to_datetime(stock_data['Date'])
    stock_data = stock_data.sort_values(by = 'Date')
    #drop the missing values
    stock_data = stock_data.dropna(subset=['Close'])
    stock_data = stock_data.reset_index(drop=True)
    return stock_data

