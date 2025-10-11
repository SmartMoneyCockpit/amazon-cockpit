import os, json
import streamlit as st
from utils import runtime

st.set_page_config(page_title="Diagnostics", page_icon="🩺", layout="wide")
st.title("🩺 Diagnostics & Smoke Tests")

with st.expander("Environment", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Python**", os.sys.version.split()[0])
        st.write("**Streamlit**", __import__("streamlit").__version__)
        st.write("**Requests**", __import__("requests").__version__)
    with c2:
        st.write("**PORT**", os.getenv("PORT"))
        st.write("**ALLOWED_ORIGINS**", ", ".join(runtime.allowed_origins()) or "∅")

ok = True
with st.expander("External connectivity", expanded=False):
    try:
        s = runtime.requests_session()
        r = s.get("https://httpbin.org/get", timeout=5)
        st.write("GET httpbin →", r.status_code)
        ok = ok and (r.status_code == 200)
    except Exception as e:
        st.error(f"Connectivity failed: {e}")
        ok = False

with st.expander("Summary", expanded=True):
    st.success("✅ Healthy") if ok and runtime.health_ok() else st.error("❌ Issues found")
