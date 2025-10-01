import streamlit as st
import pandas as pd
from utils.data import load_sample_df
from utils.layout import section_header

def finance_dashboard_view():
    section_header("💵 Finance Dashboard")
    st.caption("Revenue, COGS, Fees, Ad Spend → profitability.")
    df = load_sample_df("finance")
    df["Gross Profit"] = df["Revenue"] - df["COGS"] - df["Fees"] - df["Ad Spend"]
    st.line_chart(df.set_index("Month")[["Revenue","Gross Profit"]])
    st.dataframe(df, use_container_width=True)
    gp = int(df["Gross Profit"].sum())
    st.metric("Gross Profit (YTD)", f"${gp:,.0f}")
    st.info("Next: connect to SP‑API financial events + disbursement reports.")
