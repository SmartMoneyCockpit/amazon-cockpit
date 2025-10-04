
from __future__ import annotations
import os, json, datetime as dt
from typing import List, Dict, Any

LOG_FILE = os.path.join("logs", "vega_jobs.jsonl")

def read_jobs(path: str = LOG_FILE) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rows.append(rec)
            except Exception:
                continue
    return rows

def filter_jobs(rows: List[Dict[str, Any]], job_names=None, statuses=None, date_from=None, date_to=None):
    job_names = set(job_names or [])
    statuses = set(statuses or [])
    out = []
    for r in rows:
        j = r.get("job", "")
        s = r.get("status", "")
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
        out.append(r)
    return out
