
import streamlit as st
import pandas as pd
from utils.finance_source import read_profitability_monthly

st.set_page_config(page_title="Finance Monthly Export", layout="wide")
st.title("💾 Finance Monthly Export")

st.caption("Reads from the **profitability_monthly** tab (or /tmp CSV fallback) and lets you export filtered views.")

df = read_profitability_monthly()
if df.empty:
    st.info("No rows yet. Run **Data Sync → Refresh + Rollup + Sync to Sheets** first.")
    st.stop()

# Basic filters
months = sorted(df["month"].dropna().astype(str).unique())
sel_months = st.multiselect("Months", options=months, default=months[-1:] if months else [])
sku_text = st.text_input("Filter by SKU contains", "")

flt = df.copy()
if sel_months:
    flt = flt[flt["month"].isin(sel_months)]
if sku_text:
    flt = flt[flt["sku"].astype(str).str.contains(sku_text, case=False, na=False)]

# Derived columns
for col in ["revenue","fees","other"]:
    if col not in flt.columns:
        flt[col] = 0.0
flt["net"] = flt["revenue"].fillna(0) - flt["fees"].fillna(0) - flt["other"].fillna(0)

st.subheader("Preview")
st.dataframe(flt, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download Filtered CSV",
    data=flt.to_csv(index=False).encode("utf-8"),
    file_name="finance_profitability_monthly_filtered.csv",
    mime="text/csv"
)

st.caption("Tip: Keep this as your quick export until Ads costs are integrated into TACOS later.")
