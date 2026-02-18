import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# --- 1. Simple Moving Average ---
def generate_sma_signals(prices, short_window=20, long_window=50):
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices
    signals['short_mavg'] = prices.rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = prices.rolling(window=long_window, min_periods=1).mean()
    
    signals['signal'] = 0.0
    
    # FIX: Use .iloc for positional slicing
    # We calculate the condition for the whole series first
    condition = np.where(
        signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0
    )
    
    # Then apply it, but keep the first 'short_window' rows as 0
    signals['signal'] = condition
    signals.iloc[:short_window, signals.columns.get_loc('signal')] = 0.0
    
    signals['positions'] = signals['signal'].diff()
    return signals

# --- 2. Hybrid Strategy (SMA + RSI) ---
def generate_hybrid_signals(prices, short_window=20, long_window=50, rsi_period=14):
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices
    signals['short_mavg'] = prices.rolling(window=short_window).mean()
    signals['long_mavg'] = prices.rolling(window=long_window).mean()
    
    # RSI Calculation
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    signals['rsi'] = 100 - (100 / (1 + rs))
    
    # Logic: Buy if Trend is UP AND RSI is NOT Overbought (<70)
    signals['signal'] = 0.0
    
    # FIX: Calculate for full column, then mask the beginning
    condition = np.where(
        (signals['short_mavg'] > signals['long_mavg']) & (signals['rsi'] < 70), 1.0, 0.0
    )
    
    signals['signal'] = condition
    signals.iloc[:short_window, signals.columns.get_loc('signal')] = 0.0
    
    signals['positions'] = signals['signal'].diff()
    return signals

# --- 3. ARIMA ---
def generate_arima_signals(prices, order=(5,1,0)):
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices
    history = list(prices.values)
    
    try:
        model = ARIMA(history, order=order)
        model_fit = model.fit()
        signals['predicted_price'] = model_fit.fittedvalues
        
        signals['signal'] = np.where(signals['predicted_price'] > signals['price'], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
    except:
        print("ARIMA convergence failed, returning empty signals")
        signals['positions'] = 0.0
        
    return signals

# --- 4. LSTM ---
def run_lstm_strategy(prices, lookback=60, epochs=5):
    # Data Prep
    # Ensure we have data
    if len(prices) <= lookback:
         return pd.DataFrame(index=prices.index, columns=['positions']).fillna(0)

    data = prices.values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    # Train Model
    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)
    
    # Predict
    predicted_scaled = model.predict(X, verbose=0)
    predicted_prices = scaler.inverse_transform(predicted_scaled)
    
    # Align signals with dates
    # (Predictions start from index 'lookback')
    signals = pd.DataFrame(index=prices.index[lookback:])
    signals['price'] = prices[lookback:]
    signals['predicted'] = predicted_prices.flatten()
    
    # Generate signals based on Moving Average of the PREDICTED price
    signals['short_ma'] = signals['predicted'].rolling(window=10).mean()
    signals['long_ma'] = signals['predicted'].rolling(window=30).mean()
    
    signals['signal'] = np.where(signals['short_ma'] > signals['long_ma'], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    
    # Reindex to match original timeframe (fill early days with 0)
    full_signals = pd.DataFrame(index=prices.index)
    full_signals['positions'] = signals['positions']
    full_signals = full_signals.fillna(0.0)
    
    return full_signals