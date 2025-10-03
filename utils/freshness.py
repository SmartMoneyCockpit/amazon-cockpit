
from __future__ import annotations
import os, json, datetime as dt
from typing import Tuple, Optional

def read_etl_status(path: str | None = None) -> dict:
    path = path or os.getenv("ETL_STATUS_PATH", "/tmp/etl_status.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def parse_iso(ts: str) -> Optional[dt.datetime]:
    try:
        return dt.datetime.fromisoformat(ts.replace("Z","")).replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None

def compute_freshness(status: dict) -> Tuple[str, float]:
    ended = status.get("ended") or status.get("end") or status.get("timestamp")
    if not ended:
        return ("unknown", float("inf"))
    t = parse_iso(ended)
    if not t:
        return ("unknown", float("inf"))
    age = (dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 3600.0
    if age < 12:
        return ("green", age)
    if age < 24:
        return ("yellow", age)
    return ("red", age)
