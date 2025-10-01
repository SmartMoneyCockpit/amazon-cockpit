import os
import pandas as pd
import streamlit as st

from utils.data import get_data_sources
from utils.layout import section_header
from modules.home import dashboard_home_view
from modules.product_tracker import product_tracker_view
from modules.ppc_manager import ppc_manager_view
from modules.a_plus_seo import a_plus_seo_view
from modules.compliance_vault import compliance_vault_view
from modules.finance_dashboard import finance_dashboard_view
from modules.alerts_hub import alerts_hub_view

st.set_page_config(page_title="Amazon Cockpit", page_icon="🛒", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🛒 Amazon Cockpit")
    st.caption("Dashboard Home + Modules")
    st.divider()
    env = "production" if st.secrets.get("env") == "prod" else "staging"
    st.selectbox("Environment", ["staging", "production"], index=0 if env=="staging" else 1, key="env_select")
    st.write("**Data Sources**")
    st.json(get_data_sources(), expanded=False)
    st.divider()
    st.write("Quick Actions")
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared.")

section_header("Amazon Cockpit")
tabs = st.tabs(["Home","Product Tracker","PPC Manager","A+ & SEO","Compliance Vault","Finance Dashboard","Alerts Hub"])

with tabs[0]:
    dashboard_home_view()
with tabs[1]:
    product_tracker_view()
with tabs[2]:
    ppc_manager_view()
with tabs[3]:
    a_plus_seo_view()
with tabs[4]:
    compliance_vault_view()
with tabs[5]:
    finance_dashboard_view()
with tabs[6]:
    alerts_hub_view()

st.divider()
st.caption("© 2025 Amazon Cockpit. Home dashboard, alerts rollup, and integration health.")
