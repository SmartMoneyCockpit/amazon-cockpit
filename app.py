import os
import json
import time
import requests
import streamlit as st

# ────────────────────────────────────────────────────────────────────────────────
# Start the background scheduler (with debug)
# ────────────────────────────────────────────────────────────────────────────────
print("[boot] app.py loading…")
try:
    from services.ads_scheduler import start_scheduler
    ok = start_scheduler()
    print(f"[scheduler] launch attempted ok={ok} ENABLE_SCHEDULER={os.getenv('ENABLE_SCHEDULER')}")
except Exception as e:
    print("[scheduler] failed:", e)
    import traceback; traceback.print_exc()

# ────────────────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vega Cockpit — Settings & API",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit's default sidebar nav (we render our own accordion)
st.markdown(
    """
    <style>
      [data-testid="stSidebarNav"] { display:none !important; }
      nav[aria-label="Sidebar"] ul { display:none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
def _get_secret_like(key: str, default=None):
    """Read from st.secrets first, then env. Accepts lower/UPPER keys."""
    try:
        v = st.secrets.get(key, None)
        if v is not None:
            return v
    except Exception:
        pass
    v = os.getenv(key, None)
    if v is not None:
        return v
    # try uppercase fallback
    return os.getenv(key.upper(), default)

def _fmt(v):
    if v is None or (isinstance(v, str) and not v.strip()):
        return "—"
    if isinstance(v, (dict, list)):
        return json.dumps(v, indent=2)
    return str(v)

def _api_base() -> str:
    # Prefer secrets, then env. Example: https://amazon-cockpit-api.onrender.com
    return (_get_secret_like("API_URL", "") or "").rstrip("/")

def _api_key() -> str:
    return _get_secret_like("API_KEY", "")

def api_get(path: str, timeout: float = 15.0):
    """GET helper with x-api-key header. Returns (ok: bool, payload_or_err: Any)."""
    base = _api_base()
    if not base:
        return False, "API_URL not set. Add API_URL to Render Environment."
    url = f"{base}{path if path.startswith('/') else '/'+path}"
    headers = {}
    key = _api_key()
    if key:
        headers["x-api-key"] = key
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            # try json
            try:
                return True, r.json()
            except Exception:
                return True, r.text
        return False, f"{r.status_code} {r.text}"
    except Exception as e:
        return False, str(e)

# ────────────────────────────────────────────────────────────────────────────────
# Sidebar — Amazon-style accordion with page links (same structure you had)
# ────────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Menu")

    with st.expander("Home & Health", expanded=False):
        st.page_link("pages/00_About_and_Health.py", label="About and Health")
        st.page_link("pages/00_Home_Global_Overview.py", label="Home Global Overview")
        st.page_link("pages/01_Data_Seed.py", label="Data Seed")

    with st.expander("Product & Ads", expanded=False):
        st.page_link("pages/10_Product_Tracker.py", label="Product Tracker")
        st.page_link("pages/14_PPC_Manager_Safe.py", label="PPC Manager Safe")
        st.page_link("pages/15_PPC_Import_Wizard.py", label="PPC Import Wizard")
        st.page_link("pages/21_Aplus_Seo_Indexing.py", label="Aplus SEO Indexing")
        st.page_link("pages/21_Aplus_SEO_Panel.py", label="Aplus SEO Panel")

    with st.expander("Finance", expanded=False):
        st.page_link("pages/27_Finance_Dashboard_v2.py", label="Finance Dashboard v2")
        st.page_link("pages/26_Finance_Monthly_Export.py", label="Finance Monthly Export")
        st.page_link("pages/39_Margin_Scenario.py", label="Margin Scenario")
        st.page_link("pages/36_COGS_Manager.py", label="COGS Manager")

    with st.expander("Orders & Catalog", expanded=False):
        st.page_link("pages/28_Orders_Viewer.py", label="Orders Viewer")
        st.page_link("pages/29_Catalog_Enrichment.py", label="Catalog Enrichment")
        st.page_link("pages/38_Reorder_Forecast.py", label="Reorder Forecast")
        st.page_link("pages/24_Product_Research_Scoring.py", label="Product Research Scoring")
        st.page_link("pages/25_Data_Sync.py", label="Data Sync")

    with st.expander("Alerts & Digests", expanded=False):
        st.page_link("pages/31_Alerts_Center.py", label="Alerts Center")
        st.page_link("pages/41_Alerts_Notifications.py", label="Alerts Notifications")
        st.page_link("pages/34_Daily_Digest.py", label="Daily Digest")
        st.page_link("pages/40_Digest_Distribution.py", label="Digest Distribution")
        st.page_link("pages/33_Finance_Heatmap.py", label="Finance Heatmap")
        st.page_link("pages/32_Trade_Action_Hub.py", label="Trade Action Hub")

    with st.expander("Compliance & Vault", expanded=False):
        st.page_link("pages/22_Compliance_Vault_App.py", label="Compliance Vault App")
        st.page_link("pages/37_Revenue_Protection.py", label="Revenue Protection")
        st.page_link("pages/40_Compliance_Vault.py", label="Compliance Vault")

    with st.expander("Utilities", expanded=False):
        st.page_link("pages/35_Drive_Upload_Test.py", label="Drive Upload Test")
        st.page_link("pages/44_Settings_Controls.py", label="Settings Controls")
        st.page_link("pages/42_PPC_Live.py", label="PPC Live")

    st.header("Utilities")
    # Replace the Sheets test with an API test
    if st.button("Test API Connection"):
        ok, payload = api_get("/health")
        if ok:
            st.success(f"API health OK: {payload}")
        else:
            st.error(f"API health failed: {payload}")

# ────────────────────────────────────────────────────────────────────────────────
# Main — Settings preview (from env/secrets) + sample live call preview
# ────────────────────────────────────────────────────────────────────────────────
st.title("Vega Cockpit • Settings & API Integration")

cols = st.columns(3)
with cols[0]:
    st.metric("API URL", _fmt(_api_base()))
with cols[1]:
    st.metric("API Key set?", "Yes" if bool(_api_key()) else "No")
with cols[2]:
    # Try a lightweight live call
    ok_ping, payload_ping = api_get("/health")
    st.metric("API Health", "OK" if ok_ping else "ERROR")
    if not ok_ping and payload_ping:
        st.caption(f"Health detail: {_fmt(payload_ping)}")

st.subheader("Settings preview (env/secrets)")
settings_rows = [
    {"key": "timezone",          "value": _fmt(_get_secret_like("timezone", "America/Mazatlan"))},
    {"key": "base_currency",     "value": _fmt(_get_secret_like("base_currency", "USD"))},
    {"key": "report_start_date", "value": _fmt(_get_secret_like("report_start_date", "2025-10-02"))},
    {"key": "ads_enabled",       "value": _fmt(_get_secret_like("ads_enabled", True))},
    {"key": "auto_snapshot_pdf", "value": _fmt(_get_secret_like("auto_snapshot_pdf", True))},
    {"key": "DATABASE_URL set?", "value": "Yes" if bool(_get_secret_like("DATABASE_URL", "")) else "No"},
]
st.dataframe(settings_rows, width="stretch")

st.divider()
st.subheader("Live sample (products)")

left, right = st.columns([1,2])
with left:
    limit = st.number_input("Limit", min_value=1, max_value=200, value=10, step=1)
    if st.button("Fetch /v1/products"):
        ok, payload = api_get(f"/v1/products?limit={limit}")
        st.session_state["_last_products_resp"] = (ok, payload)
        time.sleep(0.1)

with right:
    ok, payload = st.session_state.get("_last_products_resp", (None, None))
    if ok is None:
        st.info("Click **Fetch /v1/products** to test a live DB call.")
    elif ok:
        st.success("Live data loaded")
        try:
            import pandas as pd
            if isinstance(payload, list):
                st.dataframe(pd.DataFrame(payload), width="stretch")
            else:
                st.code(_fmt(payload), language="json")
        except Exception:
            st.code(_fmt(payload), language="json")
    else:
        st.error(f"Request failed: {payload}")

# Optional: Dev tools link if present
try:
    with st.expander("Utilities", expanded=False):
        if os.path.exists("pages/45_Developer_Tools.py"):
            st.page_link("pages/45_Developer_Tools.py", label="Developer Tools")
except Exception:
    pass
