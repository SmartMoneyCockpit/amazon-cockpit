# utils/jobs_history.py
# Job history helpers: read/filter + write_job JSONL logger.

import os, json, re, time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(os.getenv("VEGA_DATA_DIR", "/data"))
LOGS_DIR_PRIMARY = DATA_DIR / "logs"
LOGS_DIR_FALLBACK = Path("/tmp/vega_data") / "logs"
ETL_STATUS = Path("/tmp/etl_status.json")

def _ensure_logs_dir():
    for d in (LOGS_DIR_PRIMARY, LOGS_DIR_FALLBACK):
        try:
            d.mkdir(parents=True, exist_ok=True)
            # test write
            p = d / ".write_test"
            p.write_text("ok", errors="ignore")
            try: p.unlink()
            except Exception: pass
            return d
        except Exception:
            continue
    # last resort
    return LOGS_DIR_FALLBACK

def _iter_log_files():
    dirs = [LOGS_DIR_PRIMARY, LOGS_DIR_FALLBACK]
    seen = set()
    for d in dirs:
        try:
            for p in d.glob("**/*"):
                if p.is_file() and p.suffix.lower() in {".log",".json"}:
                    if p not in seen:
                        seen.add(p); yield p
        except Exception:
            continue

def write_job(level: str, job: str, message: str, file: str = "", **extra):
    """Append a JSON line to ve_ga_jobs.log in a writable logs dir."""
    d = _ensure_logs_dir()
    log_path = d / "vega_jobs.log"
    entry = {
        "ts": time.time(),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "level": (level or "INFO").upper(),
        "job": job or "-",
        "message": message or "",
        "file": file or "",
    }
    if extra:
        entry.update(extra)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return str(log_path)
    except Exception as e:
        # best-effort: fallback
        try:
            fb = LOGS_DIR_FALLBACK
            fb.mkdir(parents=True, exist_ok=True)
            with open(fb / "vega_jobs.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return str(fb / "vega_jobs.log")
        except Exception:
            return ""

def read_jobs_raw():
    out = []
    if ETL_STATUS.exists():
        try:
            data = json.loads(ETL_STATUS.read_text(errors="ignore"))
            if isinstance(data, list): out.extend(data)
            else: out.append(data)
        except Exception:
            pass
    for p in _iter_log_files():
        try:
            txt = p.read_text(errors="ignore")
            if txt.strip().startswith("["):
                out.extend(json.loads(txt)); continue
            for l in [l for l in txt.splitlines() if l.strip()]:
                try:
                    out.append(json.loads(l))
                except Exception:
                    out.append({"ts": p.stat().st_mtime, "level":"INFO", "message": l, "file": str(p)})
        except Exception:
            continue
    return out

def extract_error_snippet(text: str, maxlen: int = 400):
    if not text: return ""
    text = str(text)
    m = re.search(r"(Traceback.*?$)", text, flags=re.S)
    snippet = m.group(1) if m else text
    return snippet[-maxlen:]

def read_jobs(limit: int = 200):
    rows = []
    for e in read_jobs_raw():
        ts = e.get("ts") or e.get("time") or e.get("timestamp")
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
            "level": (e.get("level") or "INFO").upper(),
            "job": e.get("job") or e.get("name") or e.get("file","-"),
            "message": e.get("message") or e.get("error") or e.get("detail") or "",
            "file": e.get("file",""),
        })
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
