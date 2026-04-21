"""
Simple in-memory + JSON file storage for analysis results.
Replace with SQLite/PostgreSQL for production scale.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import deque
import time

logger = logging.getLogger(__name__)

STORAGE_PATH = Path(__file__).parent.parent / "data" / "results.json"
STORAGE_PATH.parent.mkdir(exist_ok=True)

# In-memory ring buffer (last 500 results)
_results: deque = deque(maxlen=500)


class ResultStorage:
    @staticmethod
    def save(result_id: str, result: Dict, request: Dict) -> None:
        entry = {
            "id": result_id,
            "result": result,
            "input_preview": request.get("text", "")[:120] + "...",
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        _results.appendleft(entry)
        # Persist to disk
        try:
            with open(STORAGE_PATH, "w") as f:
                json.dump(list(_results), f, indent=2)
        except Exception as e:
            logger.warning(f"Storage write failed: {e}")

    @staticmethod
    def get_recent(limit: int = 20) -> List[Dict]:
        return list(_results)[:limit]

    @staticmethod
    def get_by_id(result_id: str) -> Optional[Dict]:
        for entry in _results:
            if entry["id"] == result_id:
                return entry
        return None

    @staticmethod
    def clear() -> None:
        _results.clear()
        if STORAGE_PATH.exists():
            STORAGE_PATH.unlink()
