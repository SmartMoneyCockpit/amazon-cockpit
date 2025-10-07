
from __future__ import annotations
import os, pathlib, datetime as dt
def env_summary():
    keys=["SHEETS_KEY","GCP_SERVICE_ACCOUNT_JSON","GOOGLE_APPLICATION_CREDENTIALS","SENDGRID_API_KEY","EMAIL_FROM","EMAIL_TO"]
    return {k: ("set" if os.getenv(k) else "missing") for k in keys}
def files_summary():
    out={}
    for p in ["snapshots","alerts",".cache","logs"]:
        path=pathlib.Path(p)
        try:
            path.mkdir(parents=True, exist_ok=True)
            test = path / "._writetest"
            test.write_text("ok"); test.unlink(missing_ok=True)
            out[p]="write_ok"
        except Exception as e:
            out[p]=f"error: {e}"
    return out
def sheets_probe():
    try:
        from infra.sheets_client import SheetsClient
        sc=SheetsClient(); 
        try: sc.read_table("Settings"); return {"status":"ok","detail":"read Settings ok"}
        except Exception as inner: return {"status":"warn","detail": f"client ok; sheet issue: {inner}"}
    except Exception as e:
        return {"status":"warn","detail": f"Sheets not configured: {e}"}
def summary():
    return {"timestamp": dt.datetime.utcnow().isoformat()+"Z", "env": env_summary(), "files": files_summary(), "sheets": sheets_probe()}
