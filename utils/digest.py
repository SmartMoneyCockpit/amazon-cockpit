from __future__ import annotations
import json, pathlib, datetime as dt

DIGEST_DIR = pathlib.Path("alerts")
DIGEST_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_FILE = DIGEST_DIR / "digest_queue.jsonl"

def enqueue(payload: dict) -> str:
    payload = dict(payload)
    payload["ts"] = dt.datetime.utcnow().isoformat() + "Z"
    with QUEUE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(QUEUE_FILE)
