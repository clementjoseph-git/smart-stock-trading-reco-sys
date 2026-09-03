import math
from statistics import pstdev


def simple_moving_average(values, window):
    if window < 1 or len(values) < window:
        raise ValueError("window must be positive and fit within the price series")
    return sum(values[-window:]) / window


def relative_strength_index(prices, period=14):
    if period < 1 or len(prices) <= period:
        raise ValueError("price series must be longer than the RSI period")
    changes = [prices[index] - prices[index - 1] for index in range(1, len(prices))]
    gains = [max(change, 0) for change in changes[-period:]]
    losses = [max(-change, 0) for change in changes[-period:]]
    average_gain = sum(gains) / period
    average_loss = sum(losses) / period
    if average_loss == 0:
        return 100.0
    return 100 - (100 / (1 + average_gain / average_loss))


def moving_average_convergence_divergence(prices, fast=12, slow=26):
    if fast < 1 or slow <= fast or len(prices) < slow:
        raise ValueError("price series and windows are invalid for MACD")
    return simple_moving_average(prices, fast) - simple_moving_average(prices, slow)


def sentiment_score(sentiment):
    positive = float(sentiment.get("Positive", sentiment.get("positive", 0)))
    negative = float(sentiment.get("Negative", sentiment.get("negative", 0)))
    neutral = float(sentiment.get("Neutral", sentiment.get("neutral", 0)))
    total = positive + negative + neutral
    if total <= 0:
        raise ValueError("sentiment scores must contain a positive total")
    return max(0.0, min(1.0, (positive + neutral * 0.5) / total))


def technical_score(prices, forecast=None):
    if len(prices) < 2:
        raise ValueError("at least two prices are required")
    if any(price <= 0 for price in prices):
        raise ValueError("prices must be positive")

    recent_change = (prices[-1] - prices[0]) / prices[0]
    score = 0.5 + recent_change * 2
    if forecast:
        forecast_change = (forecast[-1] - prices[-1]) / prices[-1]
        score += forecast_change * 2
    return max(0.0, min(1.0, score))


def volatility_score(prices):
    if len(prices) < 3:
        raise ValueError("at least three prices are required")
    returns = [
        (prices[index] - prices[index - 1]) / prices[index - 1]
        for index in range(1, len(prices))
    ]
    return max(0.0, min(1.0, pstdev(returns) * math.sqrt(252)))


def price_levels(current_price, score, volatility):
    if current_price <= 0:
        raise ValueError("current price must be positive")
    target_price = current_price * (1 + (score - 0.5) * 0.2)
    stop_distance = min(0.5, max(0.02, volatility * 1.5))
    stop_loss = current_price * (1 - stop_distance)
    return round(target_price, 4), round(stop_loss, 4)


def fundamental_score(predictions):
    if not predictions:
        raise ValueError("at least one fundamental prediction is required")
    average = sum(float(value) for value in predictions) / len(predictions)
    return 1 / (1 + math.exp(-average))
