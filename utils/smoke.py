"""
Aggregated smoke checks: sentinel, cron_validate, folders, markers, minimal file existence.
"""
import os, json
from typing import Dict

def run_all() -> Dict[str, dict]:
    out = {}
    # Sentinel
    try:
        from utils.sentinel import run_all as sentinel_run
        out["sentinel"] = {"ok": True, "data": sentinel_run(custom_env=["SENDGRID_API_KEY","DIGEST_EMAIL_FROM","DIGEST_EMAIL_TO","WEBHOOK_URL","SHEETS_KEY"])}
    except Exception as e:
        out["sentinel"] = {"ok": False, "error": str(e)}
    # Cron validate
    try:
        from utils.cron_validate import validate_all
        out["cron_validate"] = {"ok": all(r.get("ok") for r in validate_all("tools"))}
    except Exception as e:
        out["cron_validate"] = {"ok": False, "error": str(e)}
    # Folders
    for d in ["logs","backups","snapshots"]:
        try:
            os.makedirs(d, exist_ok=True)
            out[f"folder_{d}"] = {"ok": True, "exists": True, "count": len(os.listdir(d))}
        except Exception as e:
            out[f"folder_{d}"] = {"ok": False, "error": str(e)}
    # Markers
    out["marker_digest_disabled"] = {"ok": not os.path.exists(os.path.join("tools",".digest_disabled"))}
    out["marker_alerts_silenced"] = {"ok": True, "present": os.path.exists(os.path.join("logs","alerts_silenced.json"))}
    # Jobs log readable
    try:
        p = os.path.join("logs","vega_jobs.jsonl")
        ok = os.path.exists(p)
        out["jobs_log"] = {"ok": ok, "size": os.path.getsize(p) if ok else 0}
    except Exception as e:
        out["jobs_log"] = {"ok": False, "error": str(e)}
    return out
