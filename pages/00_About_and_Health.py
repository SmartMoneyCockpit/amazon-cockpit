
import os, json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="About & System Health", layout="wide")
st.title("ℹ️ About & System Health")

# ---- Versions / Mode ----
st.subheader("App Info")
st.write({
    "Streamlit": st.__version__,
    "Python": f"{os.sys.version.split()[0]}",
    "AUTH_PUBLIC_MODE": os.getenv("AUTH_PUBLIC_MODE","true"),
})

# ---- Environment checks ----
st.subheader("Environment Variables (presence only)")
env_keys = [
    "SHEETS_DOC_ID",
    "SHEETS_CREDENTIALS_JSON",
    "AMZ_LWA_CLIENT_ID", "AMZ_LWA_CLIENT_SECRET", "AMZ_REFRESH_TOKEN", "AMZ_SELLER_ID",
    "AMZ_REGION", "AMZ_MARKETPLACE_IDS",
    "ADS_ENABLED", "ADS_LWA_CLIENT_ID", "ADS_LWA_CLIENT_SECRET", "ADS_REFRESH_TOKEN", "ADS_PROFILE_ID",
    "APP_LOGIN_EMAIL", "APP_LOGIN_PASSWORD", "APP_ADMIN_EMAIL",
    "ALLOWED_ORIGINS"
]
env_table = [{"key": k, "set": ("✅" if os.getenv(k) else "—")} for k in env_keys]
st.dataframe(pd.DataFrame(env_table), use_container_width=True, hide_index=True)

# ---- Google Sheets connectivity ----
st.subheader("Google Sheets bridge")
sheets_ok = False
try:
    from utils import sheets_bridge as SB  # type: ignore
    # Try list of expected tabs
    tabs = ["inventory","product_tracker","orders","finances","keywords","competitors"]
    found = []
    for t in tabs:
        try:
            df = SB.read_tab(t)
            if isinstance(df, pd.DataFrame): found.append(t)
        except Exception:
            pass
    st.success(f"Sheets bridge: OK. Tabs reachable: {', '.join(found) if found else 'none detected'}")
    sheets_ok = True
except Exception as e:
    st.warning(f"Sheets bridge not available: {e}")

# ---- SP-API library check ----
st.subheader("Amazon SP-API library")
try:
    import sp_api  # type: ignore
    st.success("sp-api: installed")
except Exception as e:
    st.info("sp-api: not installed (pages will fall back to safe mode)")

# ---- Amazon Ads toggle ----
st.subheader("Amazon Ads (Reporting)")
ads_enabled = os.getenv("ADS_ENABLED","false").strip().lower() in ("1","true","yes")
st.write({"ADS_ENABLED": ads_enabled})
if ads_enabled:
    st.info("Remember: you also need Ads LWA client/secret + refresh token + profile id, and your app must be approved for Advertising API.")

# ---- ETL status ----
st.subheader("ETL Worker Status")
status_path = os.getenv("ETL_STATUS_PATH","/tmp/etl_status.json")
try:
    with open(status_path,"r") as f:
        status = json.load(f)
    st.json(status)
except Exception as e:
    st.info(f"No ETL status found at {status_path}. Run Data Sync once.")

# ---- Allowed origins banner ----
st.subheader("Allowed Origins")
ao = os.getenv("ALLOWED_ORIGINS","")
if ao:
    st.success(f"ALLOWED_ORIGINS: {ao}")
else:
    st.warning("ALLOWED_ORIGINS not set. Add your Render URL for hygiene.")

st.caption("This page is read-only. It checks presence of env vars (not values), basic connectivity, and shows the last ETL status file.")
