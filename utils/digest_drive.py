"""
Digest upload orchestrator:
- Generates Daily Digest PDF
- Uploads to Google Drive folder
- Appends metadata row with Drive link into the digest log Sheet
"""
from datetime import datetime
import streamlit as st

from utils.digest import generate_digest_pdf
from utils.digest_log import compute_kpis, append_digest_metadata
from utils.drive_upload import upload_bytes_pdf

def generate_upload_and_log():
    # Generate PDF
    pdf = generate_digest_pdf()
    ts = datetime.utcnow().strftime("%Y%m%d")
    fname = f"daily_digest_{ts}.pdf"

    # Upload to Drive
    folder_id = st.secrets.get("gdrive_digest_folder_id", "")
    if not folder_id:
        raise RuntimeError("Missing gdrive_digest_folder_id secret")
    meta = upload_bytes_pdf(fname, pdf, folder_id=folder_id)

    # Append metadata to Sheets with drive link
    sheet_id = st.secrets.get("gsheets_digest_log_sheet_id", "")
    if sheet_id:
        # Build a single-row DataFrame via compute_kpis plus link fields by reusing append_digest_metadata's behavior
        # Here we append an extra row with link; if you prefer to merge columns, you can adapt append_digest_metadata.
        from utils.gsheets_write import append_df
        import pandas as pd
        rec = compute_kpis()
        rec.update({"drive_file_id": meta.get("id",""), "drive_webViewLink": meta.get("webViewLink","")})
        df = pd.DataFrame([rec])
        append_df(sheet_id, "daily_digest_log", df)

    return meta, pdf, fname
