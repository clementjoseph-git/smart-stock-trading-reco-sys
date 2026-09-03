import os
from datetime import datetime, timezone

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from backend.services.market_data import MarketDataError, YahooFinanceProvider
from backend.services.market_data_storage import MarketDataStorage
from backend.services.analysis import (
    fundamental_score,
    moving_average_convergence_divergence,
    relative_strength_index,
    simple_moving_average,
    sentiment_score,
    technical_score,
    volatility_score,
    price_levels,
)
from backend.services.recommendation import generate_recommendation


class SentimentRequest(BaseModel):
    text: str = Field(min_length=1)


class ForecastRequest(BaseModel):
    data: list[float] = Field(min_length=1)


class FundamentalsRequest(BaseModel):
    X: list[list[float]] = Field(min_length=1)
    y: list[float] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_training_data(self):
        if len(self.X) != len(self.y):
            raise ValueError("X and y must contain the same number of rows")
        if not self.X[0]:
            raise ValueError("X must contain at least one feature")
        feature_count = len(self.X[0])
        if any(len(row) != feature_count for row in self.X):
            raise ValueError("X must be rectangular")
        return self


class PortfolioRequest(BaseModel):
    returns: list[float] = Field(min_length=1)
    cov_matrix: list[list[float]] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_covariance_matrix(self):
        asset_count = len(self.returns)
        if len(self.cov_matrix) != asset_count:
            raise ValueError("cov_matrix must have one row per asset")
        if any(len(row) != asset_count for row in self.cov_matrix):
            raise ValueError("cov_matrix must be square and match returns")
        return self


class RecommendationRequest(BaseModel):
    fundamental_score: float = Field(ge=0, le=1)
    technical_score: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=0, le=1)


class AnalysisRecommendationRequest(BaseModel):
    sentiment: dict[str, float]
    prices: list[float] = Field(min_length=3)
    forecast: list[float] = Field(default_factory=list)
    fundamentals: list[float] = Field(min_length=1)


def _allowed_origins():
    configured_origins = os.getenv("CORS_ORIGINS")
    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


app = FastAPI(title="Smart Stock Trading Recommendation System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentiment_model = None
forecast_model = None
fundamentals_model = None
market_data_provider = YahooFinanceProvider()
market_data_storage = MarketDataStorage()


def _get_sentiment_model():
    global sentiment_model
    if sentiment_model is None:
        from ml.sentiment.finbert_pipeline import FinBERTSentiment

        sentiment_model = FinBERTSentiment()
    return sentiment_model


def _get_forecast_model():
    global forecast_model
    if forecast_model is None:
        from ml.technicals.lstm_forecaster import LSTMForecaster

        forecast_model = LSTMForecaster()
    return forecast_model


def _get_fundamentals_model():
    global fundamentals_model
    if fundamentals_model is None:
        from ml.fundamentals.fundamentals_pipeline import FundamentalsModel

        fundamentals_model = FundamentalsModel()
    return fundamentals_model


@app.get("/")
def root():
    return {"message": "SmartTrade AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/market-data/{symbol}")
def get_market_data(
    symbol: str,
    period: str = Query("1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1m|5m|15m|30m|60m|90m|1d|5d|1wk|1mo|3mo)$"),
    persist: bool = False,
):
    try:
        if persist:
            raw_payload, normalized_data = market_data_provider.fetch_history(
                symbol, period, interval
            )
            normalized_data["persisted"] = market_data_storage.save(
                symbol, raw_payload, normalized_data
            )
            return normalized_data
        return market_data_provider.get_history(symbol, period, interval)
    except MarketDataError as error:
        status_code = 404 if str(error).startswith("Symbol not found") else 502
        raise HTTPException(status_code=status_code, detail=str(error)) from error


@app.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    return _get_sentiment_model().analyze(request.text)


@app.post("/forecast")
def forecast_stock(request: ForecastRequest):
    model_input = np.array(request.data).reshape(1, len(request.data), 1)
    prediction = _get_forecast_model().predict(model_input)
    return {"forecast": np.asarray(prediction).tolist()}


@app.post("/fundamentals")
def fundamentals_analysis(request: FundamentalsRequest):
    model = _get_fundamentals_model()
    model.train(request.X, request.y)
    prediction = model.predict(request.X)
    return {"prediction": np.asarray(prediction).tolist()}


@app.post("/portfolio")
def optimize_portfolio(request: PortfolioRequest):
    from ml.portfolio.portfolio_optimizer import PortfolioOptimizer

    optimizer = PortfolioOptimizer(request.returns, request.cov_matrix)
    weights = optimizer.optimize()
    return {"weights": np.asarray(weights).tolist()}


@app.post("/recommendation")
def recommendation(request: RecommendationRequest):
    result = generate_recommendation(
        request.fundamental_score,
        request.technical_score,
        request.sentiment_score,
    )
    return {
        "signal": result.signal,
        "confidence": result.confidence,
        "score": result.score,
        "rationale": result.rationale,
    }


@app.post("/recommendation/analyze")
def analyze_recommendation(request: AnalysisRecommendationRequest):
    derived_sentiment_score = sentiment_score(request.sentiment)
    derived_technical_score = technical_score(request.prices, request.forecast)
    derived_fundamental_score = fundamental_score(request.fundamentals)
    risk_score = volatility_score(request.prices)
    result = generate_recommendation(
        derived_fundamental_score,
        derived_technical_score,
        derived_sentiment_score * (1 - risk_score * 0.25),
    )
    target_price, stop_loss = price_levels(
        request.prices[-1], result.score, risk_score
    )
    indicators = {}
    if len(request.prices) >= 5:
        indicators["sma_5"] = round(simple_moving_average(request.prices, 5), 4)
    if len(request.prices) > 14:
        indicators["rsi_14"] = round(relative_strength_index(request.prices), 4)
    if len(request.prices) >= 26:
        indicators["macd"] = round(
            moving_average_convergence_divergence(request.prices), 4
        )
    return {
        "signal": result.signal,
        "confidence": result.confidence,
        "score": result.score,
        "rationale": result.rationale,
        "target_price": target_price,
        "stop_loss": stop_loss,
        "risk_score": round(risk_score, 4),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence": {
            "current_price": request.prices[-1],
            "forecast": request.forecast,
            "fundamentals": request.fundamentals,
            "sentiment": request.sentiment,
        },
        "scores": {
            "fundamental": round(derived_fundamental_score, 4),
            "technical": round(derived_technical_score, 4),
            "sentiment": round(derived_sentiment_score, 4),
        },
        "indicators": indicators,
    }
