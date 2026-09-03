import numpy as np
from fastapi.testclient import TestClient

from backend.api import main


client = TestClient(main.app)


class FakeSentimentModel:
    def analyze(self, text):
        return {"Positive": 0.8, "Negative": 0.1, "Neutral": 0.1}


class FakeForecastModel:
    def predict(self, model_input):
        assert model_input.shape == (1, 3, 1)
        return np.array([[101.0]])


class FakeFundamentalsModel:
    def train(self, features, targets):
        self.features = features
        self.targets = targets

    def predict(self, features):
        return np.array([10.0, 20.0])


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_market_data_returns_normalized_history(monkeypatch):
    class FakeMarketDataProvider:
        def get_history(self, symbol, period, interval):
            assert (symbol, period, interval) == ("AAPL", "5d", "1d")
            return {
                "symbol": "AAPL",
                "source": "yahoo_finance",
                "period": "5d",
                "interval": "1d",
                "data": [{"close": 100.0}],
            }

    monkeypatch.setattr(main, "market_data_provider", FakeMarketDataProvider())

    response = client.get("/market-data/AAPL?period=5d&interval=1d")

    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
    assert response.json()["data"] == [{"close": 100.0}]


def test_market_data_rejects_invalid_period():
    response = client.get("/market-data/AAPL?period=invalid")

    assert response.status_code == 422


def test_market_data_can_persist_raw_and_processed_records(monkeypatch, tmp_path):
    class FakeMarketDataProvider:
        def fetch_history(self, symbol, period, interval):
            normalized = {
                "symbol": symbol.upper(),
                "source": "yahoo_finance",
                "period": period,
                "interval": interval,
                "data": [{"close": 100.0}],
            }
            return {"provider": "fake"}, normalized

    from backend.services.market_data_storage import MarketDataStorage

    monkeypatch.setattr(main, "market_data_provider", FakeMarketDataProvider())
    monkeypatch.setattr(main, "market_data_storage", MarketDataStorage(tmp_path))

    response = client.get("/market-data/AAPL?persist=true")

    assert response.status_code == 200
    persisted = response.json()["persisted"]
    assert (tmp_path / "raw").exists()
    assert (tmp_path / "processed").exists()
    assert persisted["raw"].endswith(".json")
    assert persisted["processed"].endswith(".json")


def test_recommendation_combines_analysis_scores():
    response = client.post(
        "/recommendation",
        json={
            "fundamental_score": 0.9,
            "technical_score": 0.8,
            "sentiment_score": 0.7,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "signal": "BUY",
        "confidence": 0.63,
        "score": 0.815,
        "rationale": [
            "Positive fundamentals score",
            "Positive technical trend score",
            "Positive market sentiment score",
        ],
    }


def test_recommendation_rejects_scores_outside_range():
    response = client.post(
        "/recommendation",
        json={
            "fundamental_score": 1.2,
            "technical_score": 0.5,
            "sentiment_score": 0.5,
        },
    )

    assert response.status_code == 422


def test_structured_recommendation_derives_scores_and_indicators():
    response = client.post(
        "/recommendation/analyze",
        json={
            "sentiment": {"Positive": 0.8, "Negative": 0.1, "Neutral": 0.1},
            "prices": list(range(1, 31)),
            "forecast": [31.0, 32.0],
            "fundamentals": [1.0, 1.5],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["signal"] == "BUY"
    assert set(body["scores"]) == {"fundamental", "technical", "sentiment"}
    assert set(body["indicators"]) == {"sma_5", "rsi_14", "macd"}
    assert body["target_price"] > 0
    assert body["stop_loss"] > 0
    assert 0 <= body["risk_score"] <= 1
    assert body["generated_at"].endswith("+00:00")
    assert body["evidence"]["current_price"] == 30


def test_structured_recommendation_rejects_short_prices():
    response = client.post(
        "/recommendation/analyze",
        json={
            "sentiment": {"Positive": 1.0},
            "prices": [100.0, 101.0],
            "fundamentals": [1.0],
        },
    )

    assert response.status_code == 422


def test_sentiment_accepts_json_body(monkeypatch):
    monkeypatch.setattr(main, "sentiment_model", FakeSentimentModel())

    response = client.post("/sentiment", json={"text": "Strong earnings"})

    assert response.status_code == 200
    assert response.json()["Positive"] == 0.8


def test_forecast_accepts_json_body(monkeypatch):
    monkeypatch.setattr(main, "forecast_model", FakeForecastModel())

    response = client.post("/forecast", json={"data": [99.0, 100.0, 101.0]})

    assert response.status_code == 200
    assert response.json() == {"forecast": [[101.0]]}


def test_fundamentals_accepts_json_body(monkeypatch):
    monkeypatch.setattr(main, "fundamentals_model", FakeFundamentalsModel())

    response = client.post(
        "/fundamentals",
        json={"X": [[1.0, 2.0], [2.0, 3.0]], "y": [10.0, 20.0]},
    )

    assert response.status_code == 200
    assert response.json() == {"prediction": [10.0, 20.0]}


def test_portfolio_accepts_json_body(monkeypatch):
    class FakePortfolioOptimizer:
        def __init__(self, returns, cov_matrix):
            assert returns == [0.1, 0.2]
            assert cov_matrix == [[0.1, 0.0], [0.0, 0.1]]

        def optimize(self):
            return np.array([0.5, 0.5])

    monkeypatch.setattr(
        "ml.portfolio.portfolio_optimizer.PortfolioOptimizer",
        FakePortfolioOptimizer,
    )

    response = client.post(
        "/portfolio",
        json={
            "returns": [0.1, 0.2],
            "cov_matrix": [[0.1, 0.0], [0.0, 0.1]],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"weights": [0.5, 0.5]}


def test_invalid_matrix_shapes_are_rejected():
    fundamentals_response = client.post(
        "/fundamentals", json={"X": [[1.0, 2.0]], "y": [1.0, 2.0]}
    )
    portfolio_response = client.post(
        "/portfolio", json={"returns": [0.1, 0.2], "cov_matrix": [[0.1]]}
    )

    assert fundamentals_response.status_code == 422
    assert portfolio_response.status_code == 422
