
from __future__ import annotations
import os, json, io, datetime as dt
from typing import Optional, Tuple

def _load_credentials_from_env():
    try:
        from google.oauth2 import service_account
    except Exception:
        return None
    creds_json = os.getenv("SHEETS_CREDENTIALS_JSON", "").strip()
    if not creds_json:
        return None
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    try:
        if creds_json.startswith("{"):
            info = json.loads(creds_json)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        else:
            if os.path.exists(creds_json):
                return service_account.Credentials.from_service_account_file(creds_json, scopes=SCOPES)
    except Exception:
        return None
    return None

def _build_drive_service(creds):
    try:
        from googleapiclient.discovery import build
        return build("drive", "v3", credentials=creds, cache_discovery=False)
    except Exception:
        return None

def upload_file(path: str, mime_type: str = "application/octet-stream") -> Tuple[str, str]:
    # Upload a single file to Drive folder set by DRIVE_DIGEST_FOLDER_ID.
    if os.getenv("DRIVE_UPLOAD_ENABLED", "true").strip().lower() not in ("1","true","yes"):
        return ("skipped", "DRIVE_UPLOAD_ENABLED=false")
    folder_id = os.getenv("DRIVE_DIGEST_FOLDER_ID", "").strip()
    if not folder_id:
        return ("skipped", "DRIVE_DIGEST_FOLDER_ID not set")
    if not os.path.exists(path):
        return ("skipped", f"file not found: {path}")
    creds = _load_credentials_from_env()
    if not creds:
        return ("skipped", "SHEETS_CREDENTIALS_JSON missing or invalid for Drive scope")
    svc = _build_drive_service(creds)
    if not svc:
        return ("error", "failed to initialize drive service")
    try:
        from googleapiclient.http import MediaFileUpload
        fname = os.path.basename(path)
        file_metadata = {"name": fname, "parents": [folder_id]}
        media = MediaFileUpload(path, mimetype=mime_type, resumable=False)
        file = svc.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return ("ok", file.get("id"))
    except Exception as e:
        return ("error", str(e))

def upload_digest_for_today() -> dict:
    # Upload today's digest PDF and ZIP if present in DIGEST_OUT_DIR (default /tmp).
    outdir = os.getenv("DIGEST_OUT_DIR", "/tmp")
    tag = dt.datetime.now().strftime("%Y%m%d")
    pdf = os.path.join(outdir, f"digest_{tag}.pdf")
    zf = os.path.join(outdir, f"digest_{tag}.zip")
    res = {}
    if os.path.exists(pdf):
        res["pdf"] = upload_file(pdf, "application/pdf")
    else:
        res["pdf"] = ("skipped", "pdf not found")
    if os.path.exists(zf):
        res["zip"] = upload_file(zf, "application/zip")
    else:
        res["zip"] = ("skipped", "zip not found")
    return res
