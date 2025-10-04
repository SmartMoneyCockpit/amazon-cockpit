import streamlit as st
import pandas as pd
from infra.sheets_client import SheetsClient
from dataframes.finance import build_kpis

st.set_page_config(page_title="Finance Dashboard v2", layout="wide")

st.title("Finance Dashboard v2")

# Quiet read with graceful fallback
def _read_finances():
    try:
        sc = SheetsClient()
        rows = sc.read_table("Finances")  # expected sheet name
        return rows
    except Exception:
        return []

rows = _read_finances()
kpis, df = build_kpis(rows)

# KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("GMV (last 30d)", f"${kpis['gmv_30d']:,.0f}")
c2.metric("ACoS", f"{(kpis['acos'] or 0)*100:.1f}%")
c3.metric("TACoS", f"{(kpis['tacos'] or 0)*100:.1f}%")
c4.metric("Refund Rate", f"{(kpis['refund_rate'] or 0)*100:.2f}%")

st.divider()
st.subheader("Time Series")
st.caption("If Google Sheets is not connected, demo data is shown for preview.")

if not df.empty:
    # Show compact table + simple area chart
    with st.expander("Show raw table", expanded=False):
        st.dataframe(df.tail(60), use_container_width=True)
    st.area_chart(df.set_index("date")[["gmv"]])
else:
    st.info("No finance data available yet.")
