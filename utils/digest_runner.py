"""
Digest Runner — builds a simple daily digest, writes artifacts to backups/,
optionally emails via alerts_notify._send_email (env-guarded), and logs.
"""
from __future__ import annotations
import os
from typing import Dict, Any
from datetime import datetime as _dt

from utils.snapshot_export import save_csv, save_md_table, save_txt
from utils.jobs_history import write_job
try:
    from utils.alerts_notify import _send_email as _send_email_html
except Exception:
    _send_email_html = None

BACKUPS_DIR = "backups"

def _ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def run_digest(subject_prefix: str = "Vega Daily Digest") -> Dict[str, Any]:
    _ensure_dir(BACKUPS_DIR)
    ts = _dt.utcnow().strftime("%Y%m%d_%H%M%S")
    stamp = f"digest_{ts}"
    rows = [{"section":"info", "key":"generated_at_utc", "value": _dt.utcnow().isoformat()+"Z"}]
    csv_path = save_csv(rows, name_prefix=stamp)
    md_path  = save_md_table(rows, name_prefix=stamp)
    txt_path = save_txt(rows, name_prefix=stamp)
    out_csv = os.path.join(BACKUPS_DIR, os.path.basename(csv_path))
    out_md  = os.path.join(BACKUPS_DIR, os.path.basename(md_path))
    out_txt = os.path.join(BACKUPS_DIR, os.path.basename(txt_path))
    try:
        os.replace(csv_path, out_csv)
        os.replace(md_path,  out_md)
        os.replace(txt_path, out_txt)
    except Exception:
        pass
    sent = {"status":"skipped","message":"email_disabled"}
    html = f"<h3>{subject_prefix}</h3><ul><li>{out_csv}</li><li>{out_md}</li><li>{out_txt}</li></ul>"
    if _send_email_html:
        try:
            s, msg = _send_email_html(f"{subject_prefix}", html)
            sent = {"status": s, "message": msg}
        except Exception as e:
            sent = {"status":"error","message": str(e)}
    details = {"artifacts":[out_csv,out_md,out_txt], "email": sent}
    status = "ok" if sent.get("status") in ("ok","skipped","no_change") else "error"
    write_job("digest_run", status, details)
    return {"status": status, **details}
