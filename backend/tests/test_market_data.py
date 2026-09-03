from backend.services.market_data import MarketDataError, YahooFinanceProvider


class FakeResponse:
    status_code = 200
    ok = True

    def json(self):
        return {
            "chart": {
                "result": [
                    {
                        "timestamp": [1704067200, 1704153600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [100.0, 101.0],
                                    "high": [102.0, 103.0],
                                    "low": [99.0, 100.0],
                                    "close": [101.0, None],
                                    "volume": [1000, 1100],
                                }
                            ]
                        },
                    }
                ]
            }
        }


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def test_yahoo_provider_normalizes_ohlcv_data():
    session = FakeSession(FakeResponse())
    provider = YahooFinanceProvider(session=session)

    result = provider.get_history("aapl", period="5d", interval="1d")

    assert result["symbol"] == "AAPL"
    assert result["source"] == "yahoo_finance"
    assert len(result["data"]) == 1
    assert result["data"][0]["close"] == 101.0
    assert session.calls[0][1]["params"] == {
        "range": "5d",
        "interval": "1d",
        "events": "history",
    }


def test_yahoo_provider_rejects_invalid_payload():
    class InvalidResponse(FakeResponse):
        def json(self):
            return {"chart": {"result": []}}

    provider = YahooFinanceProvider(session=FakeSession(InvalidResponse()))

    try:
        provider.get_history("AAPL")
    except MarketDataError as error:
        assert str(error) == "Yahoo Finance returned an invalid response"
    else:
        raise AssertionError("Expected MarketDataError")
