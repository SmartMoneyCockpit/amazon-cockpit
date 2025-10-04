from __future__ import annotations
import os, json, pathlib, datetime as dt
from typing import Dict, Any

LOGS_DIR = pathlib.Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
JOBS_FILE = LOGS_DIR / "vega_jobs.jsonl"

def _ts() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"

def append_jsonl(path: pathlib.Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    if "ts" not in payload:
        payload["ts"] = _ts()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)

def log_job(name: str, status: str, detail: str = "", extra: Dict[str, Any] | None = None) -> str:
    rec = {"job": name, "status": status, "detail": detail, "ts": _ts()}
    if extra:
        rec.update(extra)
    return append_jsonl(JOBS_FILE, rec)
