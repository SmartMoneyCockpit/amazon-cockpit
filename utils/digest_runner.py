import os
from datetime import datetime as _dt
from utils.snapshot_export import save_csv, save_md_table, save_txt
from utils.jobs_history import write_job

# [51–55] Inline artifacts table and optional attachments
import os as _os
from utils.email_sendgrid_plus import send_with_optional_attachments as _send_plus

def _inline_table(paths):
    rows = "".join(f"<tr><td>{_os.path.basename(p)}</td><td>{_os.path.getsize(p) if _os.path.exists(p) else 0}</td><td>{p}</td></tr>" for p in paths if p)
    return f"<table border='1' cellspacing='0' cellpadding='4'><tr><th>Name</th><th>Size</th><th>Path</th></tr>{rows}</table>"

def send_digest_email_with_artifacts(subject_prefix: str, artifacts):
    html = f"<h3>{subject_prefix}</h3>" + _inline_table(artifacts)
    use_atts = _os.getenv("DIGEST_ATTACHMENTS","0").strip().lower() in ("1","true","yes")
    if use_atts:
        atts = [{"path": p} for p in artifacts if p and _os.path.exists(p)]
        return _send_plus(subject_prefix, html, atts)
    try:
        from utils.alerts_notify import _send_email as _send_html
        s, msg = _send_html(subject_prefix, html)
        return {"status": s, "message": msg}
    except Exception as e:
        return {"status":"error","message": str(e)}

def run_digest(subject_prefix: str = "Vega Daily Digest"):
    ts = _dt.utcnow().strftime("%Y%m%d_%H%M%S")
    stamp = f"digest_{ts}"
    rows = [{"section":"info","key":"generated_at_utc","value": _dt.utcnow().isoformat()+"Z"}]
    csv_path = save_csv(rows, name_prefix=stamp)
    md_path  = save_md_table(rows, name_prefix=stamp)
    txt_path = save_txt(rows, name_prefix=stamp)
    os.makedirs("backups", exist_ok=True)
    outs = []
    for p in (csv_path, md_path, txt_path):
        dst = os.path.join("backups", os.path.basename(p))
        try: os.replace(p, dst)
        except Exception: dst = p
        outs.append(dst)
    res = send_digest_email_with_artifacts(subject_prefix, outs)
    status = "ok" if res.get("status") in ("ok","skipped","no_change") else "error"
    write_job("digest_run", status, {"email": res, "artifacts": outs})
    return {"status": status, "email": res, "artifacts": outs}
