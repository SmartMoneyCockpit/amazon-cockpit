# utils/jobs_history.py
# Minimal job history helpers used by the Jobs History page.

import os, json, re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(os.getenv("VEGA_DATA_DIR", "/data"))
LOGS_DIR = DATA_DIR / "logs"
ETL_STATUS = Path("/tmp/etl_status.json")  # legacy path some pages expect

def _iter_log_files():
    # Accept .log or .json logs under /data/logs; fall back to /tmp
    dirs = [LOGS_DIR, Path("/tmp/vega_data")/ "logs"]
    seen = set()
    for d in dirs:
        try:
            for p in d.glob("**/*"):
                if p.is_file() and p.suffix.lower() in {".log",".json"}:
                    if p not in seen:
                        seen.add(p)
                        yield p
        except Exception:
            continue

def read_jobs_raw():
    """Return list of raw entries parsed from known log/status files."""
    out = []
    # /tmp etl status (if present)
    if ETL_STATUS.exists():
        try:
            data = json.loads(ETL_STATUS.read_text(errors="ignore"))
            if isinstance(data, list):
                out.extend(data)
            else:
                out.append(data)
        except Exception:
            pass
    # parse simple json lines logs
    for p in _iter_log_files():
        try:
            txt = p.read_text(errors="ignore")
            # Try JSON array
            if txt.strip().startswith("["):
                out.extend(json.loads(txt))
                continue
            # Try JSONL
            lines = [l for l in txt.splitlines() if l.strip()]
            for l in lines:
                try:
                    out.append(json.loads(l))
                except Exception:
                    # fallback to simple dict with message
                    out.append({"ts": p.stat().st_mtime, "level": "INFO", "message": l, "file": str(p)})
        except Exception:
            continue
    return out

def extract_error_snippet(text: str, maxlen: int = 400):
    if not text:
        return ""
    text = str(text)
    # capture last Python traceback line or common error keywords
    m = re.search(r"(Traceback.*?$)", text, flags=re.S)
    if m:
        snippet = m.group(1)[-maxlen:]
    else:
        snippet = text[-maxlen:]
    return snippet

def read_jobs(limit: int = 200):
    """Normalize raw entries to a consistent table: ts, level, job, message, file."""
    rows = []
    for e in read_jobs_raw():
        ts = e.get("ts") or e.get("time") or e.get("timestamp")
        # normalize timestamp
        try:
            if isinstance(ts, (int, float)):
                ts_str = datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(ts, str):
                ts_str = ts[:19]
            else:
                ts_str = ""
        except Exception:
            ts_str = ""
        rows.append({
            "ts": ts_str,
            "level": e.get("level","INFO"),
            "job": e.get("job") or e.get("name") or e.get("file","-"),
            "message": e.get("message") or e.get("error") or e.get("detail") or "",
            "file": e.get("file",""),
        })
    # sort by timestamp string desc
    rows.sort(key=lambda r: r.get("ts",""), reverse=True)
    return rows[:limit]

def filter_jobs(rows, levels=None, contains=None):
    levels = {lvl.upper() for lvl in (levels or [])}
    contains = (contains or "").lower().strip()
    out = []
    for r in rows:
        if levels and r.get("level","INFO").upper() not in levels:
            continue
        if contains and contains not in (r.get("message","")+r.get("job","")).lower():
            continue
        out.append(r)
    return out
