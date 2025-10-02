
import streamlit as st
from workers import etl

st.set_page_config(page_title="Data Sync", layout="wide")
st.title("🔄 Data Sync & ETL")

st.caption("Run now or view last job status. Nightly schedule will be set on Render (02:15 America/Mazatlan).")

c1, c2 = st.columns(2)
if c1.button("Refresh Orders/Inventory/Finances (Now)"):
    s = etl.run_job("refresh_orders_inventory_finances", etl.refresh_orders_inventory_finances)
    st.success(f"Ran refresh: {s}")
if c2.button("Build Monthly Profitability Rollup (Now)"):
    s = etl.run_job("monthly_profitability_rollup", etl.monthly_profitability_rollup)
    st.success(f"Ran rollup: {s}")

st.subheader("Last ETL Status")
st.json(etl.status())
