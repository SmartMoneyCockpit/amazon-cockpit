import streamlit as st
import pandas as pd
from utils.finance_source import read_profitability_monthly
from utils.finance_exporter import build_summary, export_summary_to_sheet
from utils.finance_cogs import read_cogs_map, apply_margins
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Finance Dashboard v2", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📊 Finance Dashboard v2 (Sheets-first)")
st.caption("Reads **profitability_monthly** from Google Sheets and shows KPIs. Uses `units × cogs_per_unit` for gross margin when available.")

df = read_profitability_monthly()
if df.empty:
    st.info("No data yet. Run **Data Sync → Refresh + Rollup + Sync to Sheets** first.")
    st.stop()

months = sorted(df["month"].dropna().astype(str).unique())
sel_months = st.multiselect("Months", options=months, default=months[-6:] if len(months) > 6 else months)
sku_q = st.text_input("Filter by SKU contains", "")

flt = df.copy()
if sel_months:
    flt = flt[flt["month"].isin(sel_months)]
if sku_q:
    flt = flt[flt["sku"].astype(str).str.contains(sku_q, case=False, na=False)]

# Apply COGS with units
cogs_map = read_cogs_map()
flt = apply_margins(flt, cogs_map)

for col in ["revenue","fees","other","net"]:
    if col not in flt.columns:
        flt[col] = 0.0

total_rev = float(flt["revenue"].sum())
total_fees = float(flt["fees"].sum())
total_other = float(flt["other"].sum())
total_net = float(flt["net"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue (sum)", f"${total_rev:,.2f}")
c2.metric("Fees (sum)", f"${total_fees:,.2f}")
c3.metric("Other (sum)", f"${total_other:,.2f}")
c4.metric("Net (sum)", f"${total_net:,.2f}")

summary = build_summary(flt)
st.subheader("Monthly Totals")
st.dataframe(summary, use_container_width=True, hide_index=True)

# Show units & gross margin if available
cols_to_show = ["month","sku","revenue","fees","other"]
if "units" in flt.columns: cols_to_show.append("units")
if "gross_margin_pct" in flt.columns: cols_to_show.append("gross_margin_pct")
if "net" in flt.columns: cols_to_show.append("net")

st.subheader("Detailed Rows (with Units & Gross Margin when available)")
st.dataframe(flt[cols_to_show], use_container_width=True, hide_index=True)

st.subheader("Export")
if st.button("Send Monthly Summary to Google Sheet → finance_summary"):
    res = export_summary_to_sheet(flt, tab_name="finance_summary")
    st.success(f"Exported summary: {res}")
