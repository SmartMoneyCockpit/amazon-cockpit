import streamlit as st
import pandas as pd
from datetime import date, timedelta

from utils.layout import section_header
from utils.data import load_sample_df
from utils.finance import load_finance_df, compute_profitability, kpis as finance_kpis
from utils.health import integration_health

def _kpi(name, value, help=None):
    st.metric(name, value, help=help)

def dashboard_home_view():
    st.title("🛒 Amazon Cockpit — Home")
    st.caption("Command center: KPIs, alerts, integrations, and quick links.")

    # --- Top KPIs (samples or live if configured) ---
    col1, col2, col3, col4 = st.columns(4)
    # Finance
    f_raw = load_finance_df()
    f_df = compute_profitability(f_raw)
    rev, gp, np, acos = finance_kpis(f_df)
    with col1: _kpi("Revenue (Period)", f"${rev:,.0f}")
    with col2: _kpi("Gross Profit", f"${gp:,.0f}")
    with col3: _kpi("Net Profit", f"${np:,.0f}")
    with col4: _kpi("ACoS (Period)", f"{acos:.1f}%")

    # Product health (sample)
    p_df = load_sample_df("product")
    low_doc = int((p_df["Days of Cover"] < 10).sum())
    suppressed = int((p_df.get("Suppressed?", False) == True).sum()) if "Suppressed?" in p_df.columns else 0

    col5, col6, col7, col8 = st.columns(4)
    with col5: _kpi("ASINs Tracked", len(p_df.index))
    with col6: _kpi("Low Cover (<10d)", low_doc)
    with col7: _kpi("Suppressed", suppressed)
    with col8: _kpi("Avg Stars", f"{p_df['Stars'].mean():.2f}")

    st.divider()

    # --- Alerts Summary ---
    st.subheader("🚨 Alerts Summary")
    buf = st.session_state.get("alerts_buffer", [])
    total_alerts = len(buf)
    crit = sum(1 for a in buf if a.get("severity") == "crit")
    warn = sum(1 for a in buf if a.get("severity") == "warn")
    info = sum(1 for a in buf if a.get("severity") == "info")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Total Alerts", total_alerts)
    a2.metric("Critical", crit)
    a3.metric("Warnings", warn)
    a4.metric("Info", info)

    if buf:
        with st.expander("View Recent Alerts"):
            df = pd.DataFrame(buf)
            st.dataframe(df.tail(50), use_container_width=True)

    st.divider()

    # --- Integration Health ---
    st.subheader("🔌 Integration Health")
    checks = integration_health()
    for name, status, note in checks:
        st.write(f"{status} **{name}** — {note}")

    st.divider()

    # --- Quick Links ---
    st.subheader("⚡ Quick Links")
    cols = st.columns(3)
    with cols[0]:
        st.page_link("pages/10_Product_Tracker.py", label="📦 Product Tracker", icon="📦")
        st.page_link("pages/20_PPC_Manager.py", label="📈 PPC Manager", icon="📈")
    with cols[1]:
        st.page_link("pages/30_Aplus_SEO.py", label="🧩 A+ & SEO", icon="🧩")
        st.page_link("pages/40_Compliance_Vault.py", label="🧾 Compliance Vault", icon="🧾")
    with cols[2]:
        st.page_link("pages/50_Finance_Dashboard.py", label="💵 Finance Dashboard", icon="💵")
        st.page_link("pages/60_Alerts_Hub.py", label="🚨 Alerts Hub", icon="🚨")

    st.caption("Tip: Drive the tabs to auto-populate Alerts, then come back here for a rollup.")
