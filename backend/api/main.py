from fastapi import FastAPI
from ml.sentiment.finbert_pipeline import FinBERTSentiment
from ml.technicals.lstm_forecaster import LSTMForecaster
from ml.fundamentals.fundamentals_pipeline import FundamentalsModel
from ml.portfolio.portfolio_optimizer import PortfolioOptimizer

app = FastAPI(title="Smart Stock Trading Recommendation System")

# Initialize models
sentiment_model = FinBERTSentiment()
forecast_model = LSTMForecaster()
fundamentals_model = FundamentalsModel()
# Portfolio optimizer will be initialized dynamically with data

@app.get("/")
def root():
    return {"message": "SmartTrade AI backend is running"}

@app.post("/sentiment")
def analyze_sentiment(text: str):
    return sentiment_model.analyze(text)

@app.post("/forecast")
def forecast_stock(data: list[float]):
    # Expecting a list of floats representing time-series
    import numpy as np
    X_input = np.array(data).reshape(1, len(data), 1)
    prediction = forecast_model.predict(X_input)
    return {"forecast": prediction.tolist()}

@app.post("/fundamentals")
def fundamentals_analysis(X: list[list[float]], y: list[float]):
    fundamentals_model.train(X, y)
    prediction = fundamentals_model.predict(X)
    return {"prediction": prediction.tolist()}

@app.post("/portfolio")
def optimize_portfolio(returns: list[float], cov_matrix: list[list[float]]):
    optimizer = PortfolioOptimizer(returns, cov_matrix)
    weights = optimizer.optimize()
    return {"weights": weights.tolist()}
