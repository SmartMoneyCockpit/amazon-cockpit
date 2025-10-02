
import streamlit as st
from workers import etl
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Data Sync", layout="wide")
sec.enforce()
if not gate(required_admin=True):
    st.stop()

st.title("🔄 Data Sync & ETL")

st.caption("Run now, sync to Google Sheets, or view last job status. Nightly schedule on Render (02:15/02:45 America/Mazatlan).")

c1, c2, c3 = st.columns(3)
if c1.button("Refresh Orders/Inventory/Finances (Now)"):
    s = etl.run_job("refresh_orders_inventory_finances", etl.refresh_orders_inventory_finances)
    st.success(f"Ran refresh: {s}")
if c2.button("Build Monthly Profitability Rollup (Now)"):
    s = etl.run_job("monthly_profitability_rollup", etl.monthly_profitability_rollup)
    st.success(f"Ran rollup: {s}")
if c3.button("Refresh + Rollup + Sync to Sheets"):
    s1 = etl.run_job("refresh_orders_inventory_finances", etl.refresh_orders_inventory_finances)
    s2 = etl.run_job("monthly_profitability_rollup", etl.monthly_profitability_rollup)
    st.success(f"Refresh: {s1}")
    st.success(f"Rollup: {s2}")

st.subheader("Last ETL Status")
st.json(etl.status())
