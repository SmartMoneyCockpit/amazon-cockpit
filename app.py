import os
import time
import pandas as pd
import streamlit as st

from utils.data import get_data_sources, load_sheet, load_sample_df
from utils.layout import kpi, section_header
from modules.product_tracker import product_tracker_view
from modules.ppc_manager import ppc_manager_view
from modules.a_plus_seo import a_plus_seo_view
from modules.compliance_vault import compliance_vault_view
from modules.finance_dashboard import finance_dashboard_view
from modules.alerts_hub import alerts_hub_view

st.set_page_config(page_title="Amazon Cockpit", page_icon="🛒", layout="wide")

# ==============================
# Secrets helpers (safe + friendly)
# ==============================
def get_secret(key: str, default=None):
    """Safely read st.secrets[key]; fall back to env var or default if secrets.toml is missing."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key.upper(), default)

def is_placeholder(val: str) -> bool:
    if val is None:
        return True
    v = str(val).strip()
    return (v == "") or ("placeholder" in v.lower())

def check_secrets_banner():
    """Show a sidebar banner if required secrets are missing or placeholders."""
    required = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "SPAPI_REFRESH_TOKEN",
        "SPAPI_CLIENT_ID",
        "SPAPI_CLIENT_SECRET",
        "SPAPI_ROLE_ARN",
        "REGION",
    ]
    missing_or_placeholder = []
    for k in required:
        v = get_secret(k, None)
        if is_placeholder(v):
            missing_or_placeholder.append(k)

    try:
        # Accessing st.secrets itself may raise if secrets.toml doesn't exist
        _ = bool(st.secrets)
        has_secrets_file = True
    except Exception:
        has_secrets_file = False

    if not has_secrets_file:
        st.sidebar.warning(
            "⚠️ No `.streamlit/secrets.toml` found. Using environment variables/defaults. "
            "Add a Secret File in Render to remove startup errors."
        )
    elif missing_or_placeholder:
        st.sidebar.warning(
            "⚠️ Placeholder/empty secrets detected: "
            + ", ".join(missing_or_placeholder)
            + ". Replace them in `.streamlit/secrets.toml` before going live."
        )
    else:
        st.sidebar.success("✅ Secrets loaded properly.")

# ==============================
# Sidebar
# ==============================
with st.sidebar:
    st.title("🛒 Amazon Cockpit")
    st.caption("Baseline v1")
    st.divider()

    # Determine env safely (defaults to staging)
    env_raw = get_secret("env", "staging")
    env = "production" if str(env_raw).lower() in ("prod", "production") else "staging"
    st.selectbox("Environment", ["staging", "production"], index=0 if env == "staging" else 1, key="env_select")

    # Secrets status banner
    check_secrets_banner()

    st.write("**Data Sources**")
    try:
        src = get_data_sources()
        st.json(src, expanded=False)
    except Exception as e:
        st.info("Data sources unavailable (likely placeholder creds). Running in demo mode.")

    st.divider()
    st.write("Quick filters")
    country = st.multiselect("Marketplace", ["US","CA","MX","EU","UK","JP","AU"], default=["US","CA","MX"])
    brand = st.text_input("Brand filter", value="Natural Home Cures")
    st.divider()
    st.write("Utilities")
    if st.button("🔄 Refresh data cache"):
        st.cache_data.clear()
        st.success("Cache cleared")
    st.caption("Secrets needed: SP-API (optional), Google Sheets IDs (optional).")

# ==============================
# Main content
# ==============================
section_header("Amazon Cockpit – Baseline Modules")

tab_labels = ["Product Tracker", "PPC Manager", "A+ & SEO", "Compliance Vault", "Finance Dashboard", "Alerts Hub"]
tabs = st.tabs(tab_labels)

with tabs[0]:
    product_tracker_view()

with tabs[1]:
    ppc_manager_view()

with tabs[2]:
    a_plus_seo_view()

with tabs[3]:
    compliance_vault_view()

with tabs[4]:
    finance_dashboard_view()

with tabs[5]:
    alerts_hub_view()

st.divider()
st.caption("© 2025 Amazon Cockpit (Baseline). Built with Streamlit.")
