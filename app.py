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

# --- Sidebar ---
with st.sidebar:
    st.title("🛒 Amazon Cockpit")
    st.caption("Baseline v1")
    st.divider()
    env = "production" if st.secrets.get("env") == "prod" else "staging"
    st.selectbox("Environment", ["staging", "production"], index=0 if env=="staging" else 1, key="env_select")
    st.write("**Data Sources**")
    src = get_data_sources()
    st.json(src, expanded=False)
    st.divider()
    st.write("Quick filters")
    country = st.multiselect("Marketplace", ["US","CA","MX","EU","UK","JP","AU"], default=["US","CA","MX"])
    brand = st.text_input("Brand filter", value="Natural Home Cures")
    st.divider()
    st.write("Utilities")
    if st.button("🔄 Refresh data cache"):
        st.cache_data.clear()
        st.success("Cache cleared")
    st.caption("Secrets needed: SP_API credentials (optional), Google Sheets IDs (optional).")

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
