# --- Paste into Home (near Daily Digest block) ---
from utils.digest_drive import generate_upload_and_log

st.subheader("☁️ Daily Digest → Google Drive")
ok = st.secrets.get("gdrive_digest_folder_id") and (st.secrets.get("gdrive_service_account") or st.secrets.get("gsheets_credentials"))
if not ok:
    st.info("Set `gdrive_digest_folder_id` and service account creds (`gdrive_service_account` or `gsheets_credentials`) to enable Drive upload.")
else:
    if st.button("Generate, Upload & Log"):
        try:
            meta, pdf, fname = generate_upload_and_log()
            st.success(f"Uploaded to Drive: {meta.get('name')}")
            st.write(f"Link: {meta.get('webViewLink','(not shared)')}")
            st.download_button("⬇️ Download Digest PDF", data=pdf, file_name=fname, mime="application/pdf")
        except Exception as e:
            st.error(f"Upload failed: {e}")
