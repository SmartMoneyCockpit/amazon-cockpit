# pages/Dev_Diagnostics.py
import streamlit as st
import sys, os

st.set_page_config(page_title="Developer Diagnostics", layout="wide")
st.title("🔧 Developer Diagnostics")

st.subheader("Python environment")
st.json({"python_version": sys.version})

st.subheader("Installed packages (subset)")
pkgs = {}
for name in ["gspread","google-auth","google-auth-oauthlib","google-auth-httplib2","gspread-dataframe"]:
    try:
        mod = __import__(name.replace("-","_"))
        pkgs[name] = getattr(mod, "__version__", "installed")
    except Exception as e:
        pkgs[name] = f"NOT INSTALLED ({e})"
st.json(pkgs)

st.subheader("Google Sheets bridge status")
try:
    from infra.sheets_client import sheets_status
    ok, msg = sheets_status()
    if ok:
        st.success("Sheets bridge: OK")
    else:
        st.warning(f"Sheets bridge disabled: {msg}")
except Exception as e:
    st.error(f"Sheets bridge import error: {e}")

st.subheader("Relevant env presence (masked)")
def has(k):
    return bool(os.getenv(k))
keys = [
    "SHEETS_DOC_ID","SHEETS_CREDENTIALS_JSON","SHEETS_CREDENTIALS_FILE",
    "ALLOWED_ORIGINS","VEGA_EMAIL_FROM","VEGA_EMAIL_TO"
]
st.table({"key": keys, "set": [has(k) for k in keys]})
