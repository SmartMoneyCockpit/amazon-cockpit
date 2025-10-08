

# --- [61–65] Send latest digest artifacts without regenerating ---
import os as _os, glob as _glob
def send_latest_digest(subject_prefix: str = "Vega Daily Digest (Latest)") -> dict:
    from utils.jobs_history import write_job as _write_job
    # find latest digest_* files in backups/
    _os.makedirs("backups", exist_ok=True)
    files = sorted(_glob.glob(_os.path.join("backups","digest_*.*")), key=lambda p: _os.path.getmtime(p), reverse=True)
    # keep most recent set by extension
    latest_csv = next((p for p in files if p.endswith(".csv")), None)
    latest_md  = next((p for p in files if p.endswith(".md")), None)
    latest_txt = next((p for p in files if p.endswith(".txt")), None)
    artifacts = [p for p in [latest_csv, latest_md, latest_txt] if p and _os.path.exists(p)]
    if not artifacts:
        res = {"status":"error","message":"no digest_* artifacts in backups/"}
        _write_job("digest_send_latest", "error", {"email":res})
        return res
    try:
        res = send_digest_email_with_artifacts(subject_prefix, artifacts)
        status = "ok" if res.get("status") in ("ok","skipped","no_change") else "error"
        _write_job("digest_send_latest", status, {"email":res, "artifacts":artifacts})
        return {"status": status, "email": res, "artifacts": artifacts}
    except Exception as e:
        _write_job("digest_send_latest", "error", {"error": str(e)})
        return {"status":"error","message": str(e)}
