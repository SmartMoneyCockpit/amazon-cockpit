import os, time, json
import streamlit as st
from utils import runtime

st.set_page_config(page_title="Diagnostics", page_icon="🩺", layout="wide")

st.title("🩺 Diagnostics & Smoke Tests")

with st.expander("Environment checks", expanded=True):
    cols = st.columns(2)
    with cols[0]:
        st.write("**Python version**:", os.sys.version.split()[0])
        st.write("**Working dir**:", os.getcwd())
        st.write("**PORT**:", os.getenv("PORT"))
        st.write("**Allowed Origins**:", ", ".join(runtime.allowed_origins()) or "∅")
    with cols[1]:
        st.write("**Streamlit**:", __import__("streamlit").__version__)
        st.write("**Requests**:", __import__("requests").__version__)
        st.write("**Pandas**:", __import__("pandas").__version__)

ok = True

with st.expander("External connectivity (optional)", expanded=False):
    try:
        s = runtime.get_requests_session()
        r = s.get("https://httpbin.org/get", timeout=5)
        st.write("GET https://httpbin.org/get →", r.status_code)
        ok = ok and (r.status_code == 200)
    except Exception as e:
        st.error(f"Connectivity check failed: {e}")
        ok = False

with st.expander("Health summary", expanded=True):
    st.write("Overall health:", "✅ OK" if ok and runtime.health_ok() else "❌ Issues detected")
    st.caption("This page is safe to leave in production; it doesn't expose secrets.")

st.info("Tip: Keep this page for quick triage. If you prefer, rename it under `pages/`.")
