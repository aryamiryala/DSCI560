
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def prepare_lstm_data(prices, lookback=60):
    prices = np.array(prices).reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    X, y = [], []

    for i in range(lookback, len(scaled_prices)):
        X.append(scaled_prices[i - lookback:i, 0])
        y.append(scaled_prices[i, 0])

    X = np.array(X)
    y = np.array(y)

    # reshape for LSTM: (samples, time steps, features)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    return X, y, scaler

def train_lstm(prices, lookback=60, epochs=10, batch_size=32):
    X, y, scaler = prepare_lstm_data(prices, lookback)

    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X.shape[1], 1)))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    return model, scaler

def predict_lstm(model, prices, scaler, lookback=60):
    prices = np.array(prices).reshape(-1, 1)
    scaled_prices = scaler.transform(prices)

    X = []

    for i in range(lookback, len(scaled_prices)):
        X.append(scaled_prices[i - lookback:i, 0])

    X = np.array(X)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)

    # pad beginning with NaNs so length matches original prices
    predictions = np.concatenate((np.full((lookback, 1), np.nan), predictions))

    return pd.Series(predictions.flatten())
