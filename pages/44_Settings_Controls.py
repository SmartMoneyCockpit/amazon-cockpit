import os, json, io, datetime as dt
import streamlit as st
from utils.status import summary as status_summary

st.set_page_config(page_title="Settings & Controls", layout="wide")
st.title("Settings & Controls")

tab1, tab2, tab3 = st.tabs(["System Status", "Env Keys Helper", "Diagnostics Export"])

with tab1:
    st.subheader("System Status")
    s = status_summary()
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Google Sheets**")
        st.write(s["sheets"]["status"])
        st.caption(s["sheets"]["detail"])
    with cols[1]:
        st.markdown("**Filesystem (write test)**")
        for k, v in s["files"].items():
            st.write(f"{k}: {v}")
    with cols[2]:
        st.markdown("**Environment Summary**")
        for k, v in s["env"].items():
            st.write(f"{k}: {v}")

with tab2:
    st.subheader("Env Keys Helper")
    st.caption("Copy these into Render → Environment or .streamlit/secrets.toml (secrets.toml is preferred for credentials).")

    env_col1, env_col2 = st.columns(2)
    with env_col1:
        st.code("SHEETS_KEY=<your_google_sheet_key>", language="bash")
        st.code("GCP_SERVICE_ACCOUNT_JSON=<paste full service account JSON>", language="bash")
    with env_col2:
        st.markdown("**.streamlit/secrets.toml example**")
        st.code('sheets_key = "<your_google_sheet_key>"\n'                'gcp_service_account_json = """<paste JSON here>"""', language="toml")

with tab3:
    st.subheader("Diagnostics Export")
    s = status_summary()
    buf = io.BytesIO(json.dumps(s, indent=2).encode("utf-8"))
    fname = f"vega_diagnostics_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    st.download_button("Download JSON Report", data=buf, file_name=fname, mime="application/json")
    st.caption("Attach this JSON if you ever need support. It contains only configuration status, no secrets.")

st.divider()
st.caption("This page is menu-safe and does not change your sidebar. It reuses the existing Settings & Controls slot.")


# --- [66–70] System Info (python/env/dirs) ---
import streamlit as _st
try:
    from utils.sentinel import run_all
except Exception:
    run_all = None

_st.subheader("System Info")
if run_all is None:
    _st.info("Sentinel not available.")
else:
    info = run_all(custom_env=["SENDGRID_API_KEY","DIGEST_EMAIL_FROM","DIGEST_EMAIL_TO","WEBHOOK_URL"])
    _st.json(info)
