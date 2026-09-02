import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

class LSTMForecaster:
    def __init__(self, lookback=30):
        self.lookback = lookback
        self.model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            LSTM(50),
            Dense(1)
        ])
        self.model.compile(optimizer="adam", loss="mse")

    def train(self, X_train, y_train, epochs=10):
        self.model.fit(X_train, y_train, epochs=epochs, batch_size=32)

    def predict(self, X_input):
        return self.model.predict(X_input)
