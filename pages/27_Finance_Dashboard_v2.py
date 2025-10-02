
import streamlit as st
import pandas as pd

from utils.finance_source import read_profitability_monthly
from utils.finance_exporter import build_summary, export_summary_to_sheet

st.set_page_config(page_title="Finance Dashboard v2", layout="wide")
st.title("📊 Finance Dashboard v2 (Sheets-first)")
st.caption("This dashboard reads **profitability_monthly** from Google Sheets (with /tmp CSV fallback).")

df = read_profitability_monthly()
if df.empty:
    st.info("No data yet. Run **Data Sync → Refresh + Rollup + Sync to Sheets** first.")
    st.stop()

# Filters
months = sorted(df["month"].dropna().astype(str).unique())
sel_months = st.multiselect("Months", options=months, default=months[-6:] if len(months) > 6 else months)
sku_q = st.text_input("Filter by SKU contains", "")

flt = df.copy()
if sel_months:
    flt = flt[flt["month"].isin(sel_months)]
if sku_q:
    flt = flt[flt["sku"].astype(str).str.contains(sku_q, case=False, na=False)]

# Build KPIs
for col in ["revenue","fees","other"]:
    if col not in flt.columns:
        flt[col] = 0.0
flt["net"] = flt["revenue"].fillna(0) - flt["fees"].fillna(0) - flt["other"].fillna(0)

total_rev = float(flt["revenue"].sum())
total_fees = float(flt["fees"].sum())
total_other = float(flt["other"].sum())
total_net = float(flt["net"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue (sum)", f"${total_rev:,.2f}")
c2.metric("Fees (sum)", f"${total_fees:,.2f}")
c3.metric("Other (sum)", f"${total_other:,.2f}")
c4.metric("Net (sum)", f"${total_net:,.2f}")

# Monthly trend
summary = build_summary(flt)
st.subheader("Monthly Totals")
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Export")
if st.button("Send Monthly Summary to Google Sheet → finance_summary"):
    res = export_summary_to_sheet(flt, tab_name="finance_summary")
    st.success(f"Exported summary: {res}")

# Detailed table
st.subheader("Detailed Rows")
st.dataframe(flt, use_container_width=True, hide_index=True)
