# pages/Health_Patch_Snippet.py
import streamlit as st

st.set_page_config(page_title="Health Patch Snippet", layout="wide")
st.title("Health Patch Snippet")

try:
    from services.amazon_ads_service_patch_dbdir import ensure_writable_dir
    _dir, _warn = ensure_writable_dir()
    st.info(f"Data directory in use: **{_dir}**")
    if _warn:
        st.warning(_warn)
except Exception as _e:
    st.caption(f"(Dir check skipped: {_e})")

st.success("Snippet loaded without NameError. You can keep this page or remove it after verifying the main Health page.")
