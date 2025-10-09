# pages/44_Settings_Controls_patch.py
import streamlit as st
from utils.sentinel_compat import safe_run_all

st.set_page_config(page_title="Settings & Controls (patched)", layout="wide")
st.title("Settings & Controls — System Status")

# Example custom env set the page might like to show
custom = {
    "DISK_PATH": ["VEGA_DATA_DIR"],
    "SMTP": ["SMTP_HOST","SMTP_USER","VEGA_EMAIL_FROM","VEGA_EMAIL_TO"],
}

status = safe_run_all(custom_env=custom)

# Render status blocks
gs = status.get("google_sheets", {})
fs = status.get("filesystem", {})
env = status.get("env", {})

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Google Sheets")
    st.write(gs.get("status","-"))
    st.caption(gs.get("message",""))
with col2:
    st.subheader("Filesystem (write test)")
    for k,v in fs.items():
        st.write(f"{k}: {v}")
with col3:
    st.subheader("Environment Summary")
    for k,v in env.items():
        st.write(f"{k}: {v}")

st.caption("This is a patched drop-in demo page. If your original page still imports run_all(custom_env=...), "
           "replacing utils/sentinel.py from this patch is usually sufficient.")
