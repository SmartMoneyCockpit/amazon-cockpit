
import os
import streamlit as st
from utils.auth import gate
import utils.security as sec
from utils.drive_upload import upload_digest_for_today, upload_file

st.set_page_config(page_title="Drive Upload Test", layout="wide")
sec.enforce()
if not gate(required_admin=True):
    st.stop()

st.title("☁️ Google Drive Upload — Test")
st.caption("Uses the same service account as Sheets (SHEETS_CREDENTIALS_JSON). Requires DRIVE_DIGEST_FOLDER_ID.")

st.subheader("Environment check")
env_ok = True
for key in ["SHEETS_CREDENTIALS_JSON", "DRIVE_DIGEST_FOLDER_ID"]:
    ok = bool(os.getenv(key))
    st.write(f"{key}: {'✅ set' if ok else '— missing'}")
    env_ok = env_ok and ok
st.write(f"DRIVE_UPLOAD_ENABLED={os.getenv('DRIVE_UPLOAD_ENABLED','true')} (true by default)")

st.subheader("Upload today's Digest (PDF + ZIP)")
if st.button("Upload Today’s Digest from /tmp"):
    res = upload_digest_for_today()
    st.json(res)

st.subheader("Upload arbitrary file")
path = st.text_input("Local path", "/tmp/digest_YYYYMMDD.pdf")
mime = st.text_input("MIME type", "application/pdf")
if st.button("Upload file to Drive"):
    status, msg = upload_file(path, mime)
    st.write(status, msg)

st.caption("Tip: set DRIVE_DIGEST_FOLDER_ID to your Drive folder ID. Give the service account edit permission on that folder.")
