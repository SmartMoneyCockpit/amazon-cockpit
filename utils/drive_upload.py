"""
Google Drive upload helper for PDFs (or any bytes).
Uses a Service Account to upload into a specified folder and returns file metadata.

Secrets expected:
- gdrive_service_account (JSON)  # optional; if not provided, reuse gsheets_credentials
- gdrive_digest_folder_id        # Drive folder ID to receive the PDFs

Requirements:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
"""
import io
import json
from typing import Optional, Dict
import streamlit as st

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

def _sa_info():
    blob = st.secrets.get("gdrive_service_account") or st.secrets.get("gsheets_credentials")
    if not blob:
        return None
    return blob if isinstance(blob, dict) else json.loads(blob)

def _drive_service():
    info = _sa_info()
    if not info:
        raise RuntimeError("Missing gdrive_service_account or gsheets_credentials secret")
    creds = Credentials.from_service_account_info(info, scopes=DRIVE_SCOPE)
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def upload_bytes_pdf(name: str, data: bytes, folder_id: Optional[str] = None) -> Dict[str, str]:
    service = _drive_service()
    file_metadata = {"name": name}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="application/pdf", resumable=False)
    file = service.files().create(body=file_metadata, media_body=media, fields="id, name, webViewLink, webContentLink").execute()
    # Make link shareable (optional): set permission anyoneWithLink reader
    try:
        service.permissions().create(fileId=file["id"], body={"role": "reader", "type": "anyone"}).execute()
        # Re-fetch to ensure webViewLink is available
        file = service.files().get(fileId=file["id"], fields="id, name, webViewLink, webContentLink").execute()
    except Exception:
        pass
    return file
