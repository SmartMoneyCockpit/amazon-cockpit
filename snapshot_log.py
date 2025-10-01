"""
Snapshot + Log entry point:
- Generates the Daily Digest PDF (from utils.digest)
- If `gsheets_digest_log_sheet_id` secret is set, appends a metadata row

Run:
    streamlit run snapshot_log.py
"""
import streamlit as st
from datetime import datetime
from utils.digest import generate_digest_pdf
from utils.digest_log import append_digest_metadata

st.title("📄 Daily Digest + Sheets Log")
pdf = None

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Digest PDF"):
        pdf = generate_digest_pdf()
        st.session_state["digest_pdf"] = pdf
        st.success("Digest generated.")

with col2:
    sheet_id = st.secrets.get("gsheets_digest_log_sheet_id", "")
    if st.button("Append Metadata to Sheets"):
        if not sheet_id:
            st.error("Set secret `gsheets_digest_log_sheet_id` to enable logging.")
        else:
            n = append_digest_metadata(sheet_id, worksheet="daily_digest_log")
            st.success(f"Appended {n} row(s) to daily_digest_log.")

# Download if available
pdf = st.session_state.get("digest_pdf")
if pdf:
    ts = datetime.utcnow().strftime("%Y%m%d")
    st.download_button("⬇️ Download Daily Digest PDF", data=pdf, file_name=f"daily_digest_{ts}.pdf", mime="application/pdf")
