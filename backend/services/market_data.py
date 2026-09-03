from datetime import datetime, timezone

import requests


class MarketDataError(Exception):
    """Raised when a market-data provider cannot return valid data."""


class YahooFinanceProvider:
    endpoint = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self, session=None, timeout=10):
        self.session = session or requests
        self.timeout = timeout

    def get_history(self, symbol, period="1mo", interval="1d"):
        _, normalized_data = self.fetch_history(symbol, period, interval)
        return normalized_data

    def fetch_history(self, symbol, period="1mo", interval="1d"):
        response = self.session.get(
            f"{self.endpoint}/{symbol.upper()}",
            params={"range": period, "interval": interval, "events": "history"},
            timeout=self.timeout,
        )
        if response.status_code == 404:
            raise MarketDataError(f"Symbol not found: {symbol}")
        if not response.ok:
            raise MarketDataError(f"Yahoo Finance returned HTTP {response.status_code}")

        try:
            payload = response.json()
            result = payload["chart"]["result"][0]
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
        except (KeyError, IndexError, TypeError):
            raise MarketDataError("Yahoo Finance returned an invalid response") from None

        records = []
        for index, timestamp in enumerate(timestamps):
            close = quotes.get("close", [])[index]
            if close is None:
                continue
            records.append(
                {
                    "timestamp": datetime.fromtimestamp(
                        timestamp, tz=timezone.utc
                    ).isoformat(),
                    "open": quotes.get("open", [])[index],
                    "high": quotes.get("high", [])[index],
                    "low": quotes.get("low", [])[index],
                    "close": close,
                    "volume": quotes.get("volume", [])[index],
                }
            )

        if not records:
            raise MarketDataError(f"No market data available for: {symbol}")

        normalized_data = {
            "symbol": symbol.upper(),
            "source": "yahoo_finance",
            "period": period,
            "interval": interval,
            "data": records,
        }
        return payload, normalized_data
