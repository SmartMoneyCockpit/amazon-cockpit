"""
Standalone entry point to generate Daily Digest PDF.
Usage: streamlit run snapshot.py
"""
import streamlit as st
from utils.digest import generate_digest_pdf

st.title("📄 Daily Digest Snapshot")
if st.button("Generate Now"):
    pdf = generate_digest_pdf()
    st.download_button("Download Digest PDF", pdf, file_name="daily_digest.pdf", mime="application/pdf")
    st.success("Digest generated.")
else:
    st.info("Click the button to generate today's digest.")
