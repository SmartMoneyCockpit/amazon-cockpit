# pages/27_Finance_Dashboard_v2.py
from __future__ import annotations
import time
import streamlit as st
import pandas as pd

from utils.finance_db import fetch_finance_snapshot, kpis

st.set_page_config(
    page_title="Vega Cockpit — Finance Dashboard (Live)",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💵 Finance Dashboard (Live)")

# Controls
ctrl = st.columns([1,1,2])
with ctrl[0]:
    limit = st.number_input("Rows to pull", 50, 5000, 500, step=50)
with ctrl[1]:
    if st.button("🔄 Refresh (live)"):
        st.session_state["_finance_df"] = fetch_finance_snapshot(limit=limit)
        time.sleep(0.05)

# Load (first load or from session)
df = st.session_state.get("_finance_df", fetch_finance_snapshot(limit=limit))

# KPIs
c1, c2, c3, c4 = st.columns(4)
rev, gp, np, acos = kpis(df)
with c1: st.metric("Revenue",      f"${rev:,.2f}")
with c2: st.metric("Gross Profit", f"${gp:,.2f}")
with c3: st.metric("Net Profit",   f"${np:,.2f}")
with c4: st.metric("ACoS %",       f"{acos:,.2f}%")

st.divider()
st.subheader("Finance Snapshot")
if df.empty:
    st.info("No data yet. As your ingestion populates orders/finance, this view updates automatically.")
else:
    st.dataframe(df, use_container_width=True, height=480)

st.caption(
    "This page currently derives a minimal finance snapshot from products. "
    "When the `/v1/finance` endpoint is added, we'll switch the data source to your "
    "actual order/finance tables for precise KPIs."
)
