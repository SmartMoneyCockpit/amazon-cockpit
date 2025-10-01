"""
Run:
    streamlit run snapshot_drive.py
"""
import streamlit as st
from utils.digest_drive import generate_upload_and_log

st.title("📄 Daily Digest → Google Drive + Sheets Log")
if st.button("Generate, Upload & Log"):
    try:
        meta, pdf, fname = generate_upload_and_log()
        st.success(f"Uploaded: {meta.get('name')}")
        if meta.get("webViewLink"):
            st.write("Drive Link:", meta.get("webViewLink"))
        st.download_button("⬇️ Download Digest PDF", data=pdf, file_name=fname, mime="application/pdf")
    except Exception as e:
        st.error(f"Failed: {e}")
else:
    st.info("Click to generate the digest, upload it to Google Drive, and append metadata to the Sheet.")
