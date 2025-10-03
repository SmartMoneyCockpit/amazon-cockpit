
import os
import streamlit as st
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Daily Digest", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📥 Owner’s Daily Digest")
st.caption("Generate and download today's tight 1‑page PDF and full CSV pack.")

colA, colB = st.columns(2)
if colA.button("Generate Now"):
    try:
        from scripts import daily_digest
        res = daily_digest.generate()
        st.success("Digest generated.")
        st.session_state["_digest_paths"] = res
    except Exception as e:
        st.error(f"Failed to generate digest: {e}")

paths = st.session_state.get("_digest_paths")
if not paths:
    import datetime as dt
    tag = dt.datetime.now().strftime("%Y%m%d")
    pdf_guess = f"/tmp/digest_{tag}.pdf"
    zip_guess = f"/tmp/digest_{tag}.zip"
    if os.path.exists(pdf_guess) or os.path.exists(zip_guess):
        paths = {"pdf": pdf_guess if os.path.exists(pdf_guess) else None,
                 "zip": zip_guess if os.path.exists(zip_guess) else None}

st.subheader("Downloads")
if paths and paths.get("pdf") and os.path.exists(paths["pdf"]):
    with open(paths["pdf"], "rb") as f:
        st.download_button("⬇️ Download PDF", f, file_name=os.path.basename(paths["pdf"]), mime="application/pdf")
else:
    st.info("PDF not found yet (install reportlab to enable PDF output).")

if paths and paths.get("zip") and os.path.exists(paths["zip"]):
    with open(paths["zip"], "rb") as f:
        st.download_button("⬇️ Download CSV Pack (ZIP)", f, file_name=os.path.basename(paths["zip"]), mime="application/zip")
else:
    st.info("ZIP not found yet. Use Generate Now or wait for morning snapshot.")
