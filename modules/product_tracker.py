import streamlit as st
import pandas as pd
from utils.data import load_sheet, load_sample_df
from utils.layout import section_header

def product_tracker_view():
    section_header("📦 Product Tracker")
    st.caption("Sessions, CVR, units, inventory, reviews. Replace sample data with SP‑API/Sheets later.")
    df = load_sample_df("product")
    st.dataframe(df, use_container_width=True)
    kpis = st.columns(4)
    kpis[0].metric("Total Units (14d)", int(df["Units"].sum()))
    kpis[1].metric("Avg CVR", f"{df['CVR%'].mean():.1f}%")
    kpis[2].metric("Avg Stars", f"{df['Stars'].mean():.2f}")
    kpis[3].metric("At Risk (<10 DoC)", int((df['Days of Cover']<10).sum()))
    st.info("Next: wire to SP‑API 'getCatalogItems' + 'getSalesAndTraffic' or Sheets mirror.")
