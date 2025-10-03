
import streamlit as st
import pandas as pd

from utils.auth import gate
import utils.security as sec
from utils.margin_simulator import load_base, simulate
from utils.sheets_writer import write_df

st.set_page_config(page_title="Margin Scenario Simulator", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("🧪 Margin Scenario Simulator")

base = load_base()
if base.empty:
    st.info("No data found in 'profitability_monthly'. Run Data Sync first or seed data.")
    st.stop()

st.sidebar.header("Scenario Deltas (%)")
price_change = st.sidebar.number_input("Price change %", -90.0, 500.0, 0.0, 0.5)
cogs_change = st.sidebar.number_input("COGS per unit change %", -90.0, 500.0, 0.0, 0.5)
fees_change = st.sidebar.number_input("Fees change %", -90.0, 500.0, 0.0, 0.5)
ppc_change = st.sidebar.number_input("PPC/Other change %", -90.0, 500.0, 0.0, 0.5)

# Optional COGS mapping from cogs_map
cogs_map = None
try:
    from utils import sheets_bridge as SB
    cogs_map = SB.read_tab("cogs_map")
except Exception:
    cogs_map = None

res = simulate(base,
               price_change_pct=price_change,
               cogs_per_unit_change_pct=cogs_change,
               fees_change_pct=fees_change,
               ppc_change_pct=ppc_change,
               cogs_per_unit_map=cogs_map)

# KPIs
total_net_base = float(res["net_base"].sum()) if "net_base" in res.columns else 0.0
total_net_new = float(res["net_new"].sum()) if "net_new" in res.columns else 0.0
delta = total_net_new - total_net_base

c1,c2,c3 = st.columns(3)
c1.metric("Net (Base)", f"${total_net_base:,.2f}")
c2.metric("Net (Scenario)", f"${total_net_new:,.2f}")
c3.metric("Δ Net", f"${delta:,.2f}")

st.subheader("Scenario Table")
st.dataframe(res, use_container_width=True, hide_index=True)

cA,cB = st.columns(2)
if cA.button("📤 Export Scenario → Sheet (scenarios_out)"):
    st.success(write_df("scenarios_out", res))

st.download_button("⬇️ Download Scenario (CSV)",
                   data=res.to_csv(index=False).encode("utf-8"),
                   file_name="margin_scenario.csv",
                   mime="text/csv")
