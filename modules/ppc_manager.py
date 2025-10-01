import streamlit as st
import pandas as pd
from utils.data import load_sample_df
from utils.layout import section_header

def ppc_manager_view():
    section_header("📈 PPC Manager")
    st.caption("Budgets, ACoS, ROAS, and campaign drill‑downs.")
    df = load_sample_df("ppc")
    st.line_chart(df.set_index("Date")[["Impressions","Clicks","Orders"]])
    st.area_chart(df.set_index("Date")[["Spend"]])
    st.bar_chart(df.set_index("Date")[["ROAS"]])
    st.dataframe(df, use_container_width=True)
    cols = st.columns(3)
    cols[0].metric("Avg ACoS", f"{df['ACoS%'].mean():.1f}%")
    cols[1].metric("Avg ROAS", f"{df['ROAS'].mean():.2f}")
    cols[2].metric("Spend (14d)", f"${df['Spend'].sum():,.0f}")
    st.info("Next: connect to Amazon Ads API (SP‑API Advertising) or ingest from Sheets export.")
