"""
Lightweight JSONL jobs history utilities (fixed for filters & exports).
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

def filter_jobs(rows: List[Dict[str, Any]], job_names=None, statuses=None, date_from=None, date_to=None, text=None):
    job_names = set(job_names or [])
    statuses = set(statuses or [])
    out: List[Dict[str, Any]] = []
    text_l = (text or "").strip().lower()
    for r in rows:
        j = (r.get("job","") or "")
        s = (r.get("status","") or "")
        ts = r.get("ts")
        try:
            dtobj = dt.datetime.fromisoformat((ts or "").replace("Z",""))
        except Exception:
            dtobj = None
        if job_names and j not in job_names: 
            continue
        if statuses and s not in statuses: 
            continue
        if date_from and dtobj and dtobj.date() < date_from: 
            continue
        if date_to and dtobj and dtobj.date() > date_to: 
            continue
        if text_l:
            blob = json.dumps(r, ensure_ascii=False).lower()
            if text_l not in blob:
                continue
        out.append(r)
    return out

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
