"""
JSONL jobs history utilities (stable).
"""
from __future__ import annotations
import os, json, datetime as dt
from typing import List, Dict, Any

LOG_FILE = os.path.join("logs", "vega_jobs.jsonl")

def read_jobs(path: str = LOG_FILE) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows

def write_job(job: str, status: str, details: dict=None, path: str=LOG_FILE) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    rec = {
        "ts": dt.datetime.utcnow().isoformat() + "Z",
        "job": job,
        "status": status,
        "details": details or {},
    }
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False
