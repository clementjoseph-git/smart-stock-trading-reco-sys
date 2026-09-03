import json
from datetime import datetime, timezone
from pathlib import Path


class MarketDataStorage:
    def __init__(self, data_root=None):
        self.data_root = Path(data_root or "data")

    def save(self, symbol, raw_payload, normalized_data):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{symbol.upper()}_{timestamp}.json"
        raw_path = self.data_root / "raw" / filename
        processed_path = self.data_root / "processed" / filename

        self._write_json(raw_path, raw_payload)
        self._write_json(processed_path, normalized_data)

        return {
            "raw": str(raw_path),
            "processed": str(processed_path),
        }

    @staticmethod
    def _write_json(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
