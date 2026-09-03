import json

from backend.services.market_data_storage import MarketDataStorage


def test_storage_writes_raw_and_processed_json(tmp_path):
    storage = MarketDataStorage(tmp_path)

    paths = storage.save(
        "aapl",
        {"raw": True},
        {"symbol": "AAPL", "data": [{"close": 100.0}]},
    )

    assert json.loads((tmp_path / "raw" / paths["raw"].split("\\")[-1]).read_text()) == {
        "raw": True
    }
    assert json.loads(
        (tmp_path / "processed" / paths["processed"].split("\\")[-1]).read_text()
    )["symbol"] == "AAPL"