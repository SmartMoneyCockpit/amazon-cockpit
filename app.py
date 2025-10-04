import os
import streamlit as st
from infra.sheets_client import SheetsClient
st.set_page_config(page_title="Vega Cockpit", layout="wide", initial_sidebar_state="expanded")

st.set_page_config(
    page_title="Vega Cockpit - Google Sheets",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit default nav so only our accordion appears
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display:none !important; }
    nav[aria-label="Sidebar"] ul { display:none !important; }
    </style>
    """, unsafe_allow_html=True,
)

# ---------------- Sidebar: Amazon-style accordion with page links ----------------
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
    if st.button("Test Google Sheets Connection"):
        try:
            sc = SheetsClient()
            _ = sc.read_table("Settings")
            st.success("Sheets connection OK.")
        except Exception as e:
            st.error(f"Connection test failed: {e}")

# ---------------- Main: Settings preview with defaults fallback ----------------
st.title("Vega Cockpit • Google Sheets Integration")
st.subheader("Settings preview")

def _get(k, d=None):
    try:
        return st.secrets.get(k, d)
    except Exception:
        return os.getenv(k.upper(), d)

def _fmt(v):
    if v is None or v == "":
        return "—"
    return str(v)

try:
    sc = SheetsClient()
    rows = sc.read_table("Settings")
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("No rows yet in 'Settings'.")
except Exception:
    import pandas as pd
    data = [
        {"key": "timezone", "value": _fmt(_get("timezone", "America/Mazatlan"))},
        {"key": "base_currency", "value": _fmt(_get("base_currency", "USD"))},
        {"key": "report_start_date", "value": _fmt(_get("report_start_date", "2025-10-02"))},
        {"key": "ads_enabled", "value": _fmt(_get("ads_enabled", True))},
        {"key": "auto_snapshot_pdf", "value": _fmt(_get("auto_snapshot_pdf", True))},
    ]
    st.caption("Defaults loaded; connect Google Sheets or set secrets/env to override.")
    st.dataframe(pd.DataFrame(data), use_container_width=True)