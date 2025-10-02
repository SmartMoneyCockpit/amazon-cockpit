
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.auth import gate
import utils.security as sec
from utils.finance_source import read_profitability_monthly
from utils.finance_cogs import read_cogs_map, apply_margins

st.set_page_config(page_title="Finance Heatmap", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📊 Finance Heatmap (Margins)")
st.caption("Visualize gross/net margins by SKU × Month. Colors highlight problem areas.")

# Load data
df = read_profitability_monthly()
if df.empty:
    st.info("No profitability data yet. Run Data Sync and rollup first.")
    st.stop()

# Apply COGS if available
cogs_map = read_cogs_map()
df = apply_margins(df, cogs_map)

if "month" not in df.columns:
    st.warning("No month column in data.")
    st.stop()

# Filter months
months = sorted(df["month"].dropna().astype(str).unique())
sel_months = st.multiselect("Months", months, default=months[-6:] if len(months) > 6 else months)

flt = df.copy()
if sel_months:
    flt = flt[flt["month"].isin(sel_months)]

if flt.empty:
    st.warning("No data for selected months.")
    st.stop()

# Build pivot table for gross margin %
if "gross_margin_pct" not in flt.columns:
    st.info("COGS not provided. Only net margin available.")
    flt["gross_margin_pct"] = flt.get("net_margin_pct", np.nan)

pivot = flt.pivot_table(index="sku", columns="month", values="gross_margin_pct", aggfunc="mean")

st.subheader("Heatmap: Gross Margin %")
fig, ax = plt.subplots(figsize=(10, max(4, len(pivot)//2)))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", center=30, cbar_kws={'label': 'Gross Margin %'}, ax=ax)
st.pyplot(fig)

# Net margin heatmap if available
if "net_margin_pct" in flt.columns:
    pivot2 = flt.pivot_table(index="sku", columns="month", values="net_margin_pct", aggfunc="mean")
    st.subheader("Heatmap: Net Margin %")
    fig2, ax2 = plt.subplots(figsize=(10, max(4, len(pivot2)//2)))
    sns.heatmap(pivot2, annot=True, fmt=".1f", cmap="RdYlGn", center=10, cbar_kws={'label': 'Net Margin %'}, ax=ax2)
    st.pyplot(fig2)

st.caption("Tip: Add a `cogs_map` tab to Sheets (sku,cogs_per_unit) to enable accurate gross margin calculations.")
