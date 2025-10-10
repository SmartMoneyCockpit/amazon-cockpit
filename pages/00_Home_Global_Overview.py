# pages/00_Home_Global_Overview.py
from __future__ import annotations
import time
import streamlit as st
import pandas as pd

from utils.api_client import health, list_products

st.set_page_config(
    page_title="Vega Cockpit — Global Overview (Live)",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏠 Global Overview (Live)")
st.caption("This page pulls directly from the API/DB via utils/api_client.py")

# ────────────────────────────────────────────────────────────────────────────────
# Health + live fetch helpers
# ────────────────────────────────────────────────────────────────────────────────
def fetch_products(limit: int = 100):
    ok, data = list_products(limit=limit)
    if not ok:
        st.error(f"API error: {data}")
        return pd.DataFrame()
    if isinstance(data, list) and data:
        # normalize into a frame
        df = pd.DataFrame(data)
        # keep a stable column order if present
        cols = [c for c in ["id", "asin", "title", "price"] if c in df.columns]
        return df[cols] if cols else df
    return pd.DataFrame(columns=["id", "asin", "title", "price"])

# ────────────────────────────────────────────────────────────────────────────────
# Health section
# ────────────────────────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([1,3])
with hcol1:
    ok_health, payload_health = health()
    st.metric("API Health", "OK" if ok_health else "ERROR")
with hcol2:
    with st.expander("Health detail", expanded=not ok_health):
        st.write(payload_health)

st.divider()

# ────────────────────────────────────────────────────────────────────────────────
# Live KPIs (based on current products table — adjust as you add more data)
# ────────────────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
limit = st.number_input("Max rows to pull", 10, 2000, 200, step=10)

if st.button("🔄 Refresh (live)"):
    st.session_state["_global_products_df"] = fetch_products(limit=limit)
    time.sleep(0.05)

df = st.session_state.get("_global_products_df", fetch_products(limit=limit))

with c1:
    st.metric("Products", int(df.shape[0]))
with c2:
    avg_price = float(df["price"].dropna().mean()) if "price" in df.columns else 0.0
    st.metric("Avg Price", f"${avg_price:,.2f}")
with c3:
    priced = int(df["price"].notna().sum()) if "price" in df.columns else 0
    st.metric("With Price", priced)
with c4:
    missing_price = int(df.shape[0] - priced)
    st.metric("Missing Price", missing_price)

st.subheader("Inventory Snapshot (from DB)")
st.dataframe(df, use_container_width=True, height=420)

st.caption(
    "Tip: As you ingest more data (orders, finance, ads), we’ll extend this page’s KPIs "
    "to include revenue/COGS/fees and add charts fed by new API endpoints."
)
