
from __future__ import annotations
import os, json, pathlib, datetime as dt
from typing import Dict, Any

NEEDED_ENV = [
    "SHEETS_KEY",
    "GCP_SERVICE_ACCOUNT_JSON",   # or GOOGLE_APPLICATION_CREDENTIALS
    "GOOGLE_APPLICATION_CREDENTIALS",
]

def env_summary() -> Dict[str, Any]:
    ok = {}
    for key in NEEDED_ENV:
        val = os.getenv(key)
        present = bool(val and str(val).strip())
        ok[key] = "set" if present else "missing"
    return ok

def files_summary() -> Dict[str, Any]:
    out = {}
    for p in ["snapshots", "alerts", ".cache"]:
        path = pathlib.Path(p)
        try:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / f"._writetest_{dt.datetime.utcnow().timestamp()}"
            test_file.write_text("ok")
            test_file.unlink(missing_ok=True)
            out[p] = "write_ok"
        except Exception as e:
            out[p] = f"error: {e}"
    return out

def sheets_probe() -> Dict[str, Any]:
    try:
        from infra.sheets_client import SheetsClient
        sc = SheetsClient()
        try:
            _ = sc.read_table("Settings")
            return {"status": "ok", "detail": "read Settings ok"}
        except Exception as inner:
            return {"status": "warn", "detail": f"client ok; sheet issue: {inner}"}
    except Exception as e:
        return {"status": "warn", "detail": f"Sheets not configured: {e}"}

def summary() -> Dict[str, Any]:
    return {
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "env": env_summary(),
        "files": files_summary(),
        "sheets": sheets_probe(),
    }
