
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
from utils.reorder_forecast import build_reorder_plan
from utils.sheets_writer import write_df

st.set_page_config(page_title="Reorder Forecast", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📦 Reorder Forecast")

st.sidebar.header("Parameters")
lookback_days = st.sidebar.number_input("Sales lookback (days)", 7, 180, 60, 1)
lead_time_days = st.sidebar.number_input("Lead time (days)", 1, 180, 21, 1)
safety_stock_days = st.sidebar.number_input("Safety stock (days)", 0, 60, 7, 1)
moq_units = st.sidebar.number_input("MOQ (units)", 0, 100000, 0, 1)

df = build_reorder_plan(lookback_days=lookback_days,
                        lead_time_days=lead_time_days,
                        moq_units=moq_units,
                        safety_stock_days=safety_stock_days)

if df.empty:
    st.info("No data yet. Ensure `orders` and `inventory` tabs exist (use Data Seed if needed).")
else:
    # KPIs
    red = int((df["priority"]=="red").sum())
    yel = int((df["priority"]=="yellow").sum())
    tot = len(df)
    c1,c2,c3 = st.columns(3)
    c1.metric("Critical (<= lead time)", red)
    c2.metric("Attention (<= lead+safety)", yel)
    c3.metric("Total SKUs", tot)

    st.subheader("Plan")
    st.dataframe(df, use_container_width=True, hide_index=True)

    cA,cB = st.columns(2)
    if cA.button("📤 Export plan → Sheet (reorder_plan)"):
        st.success(write_df("reorder_plan", df))
    cB.download_button("⬇️ Download CSV", data=df.to_csv(index=False).encode("utf-8"),
                       file_name="reorder_plan.csv", mime="text/csv")
