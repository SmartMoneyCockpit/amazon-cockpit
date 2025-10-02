
"""Lightweight ETL worker skeleton.
This module intentionally avoids dependencies. Wire this into a Render cron job later.
"""
from __future__ import annotations
import json, time, os, traceback, datetime as dt

STATUS_PATH = os.environ.get("ETL_STATUS_PATH", "/tmp/etl_status.json")

def _write_status(status: dict):
    try:
        with open(STATUS_PATH, "w") as f:
            json.dump(status, f)
    except Exception:
        pass

def run_job(name: str, fn, *args, **kwargs):
    started = dt.datetime.utcnow().isoformat()
    try:
        fn(*args, **kwargs)
        status = {"job": name, "status": "ok", "started": started, "ended": dt.datetime.utcnow().isoformat()}
    except Exception as e:
        status = {"job": name, "status": "error", "started": started, "ended": dt.datetime.utcnow().isoformat(),
                  "error": str(e), "trace": traceback.format_exc()}
    _write_status(status)
    return status

# Example no-op tasks
def warm_cache():
    time.sleep(0.1)

def refresh_rollups():
    time.sleep(0.1)

if __name__ == "__main__":
    # Run both for local testing
    print(run_job("warm_cache", warm_cache))
    print(run_job("refresh_rollups", refresh_rollups))
