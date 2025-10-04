import datetime as dt
import pandas as pd
import streamlit as st
from infra.sheets_client import SheetsClient
from utils.orders_tools import demo_orders, normalize, kpis

st.set_page_config(page_title="Orders Viewer", layout="wide")
st.title("Orders Viewer")

@st.cache_data(show_spinner=False, ttl=300)
def _read_orders():
    try:
        sc = SheetsClient()
        rows = sc.read_table("Orders")
        return normalize(pd.DataFrame(rows))
    except Exception:
        return normalize(demo_orders())

d = _read_orders()

# Filters
c1, c2, c3, c4 = st.columns([1.2,1.2,1,1.6])
with c1:
    start = st.date_input("Start", value=(dt.date.today() - dt.timedelta(days=30)))
with c2:
    end = st.date_input("End", value=dt.date.today())
with c3:
    countries = sorted([x for x in d["country"].dropna().unique().tolist() if x])
    sel_country = st.multiselect("Country", countries, default=countries)
with c4:
    query = st.text_input("ASIN / SKU contains", value="")

mask = (d["date"] >= start) & (d["date"] <= end)
if sel_country:
    mask &= d["country"].isin(sel_country)
if query:
    q = query.lower()
    mask &= (d["asin"].fillna("").str.lower().str.contains(q) | d["sku"].fillna("").str.lower().str.contains(q))

df = d.loc[mask].copy()

# KPIs
m = kpis(df)
k1, k2, k3 = st.columns(3)
k1.metric("Orders", f"{m['orders']:,}")
k2.metric("Revenue", f"${m['revenue']:,.2f}")
k3.metric("Avg Order Value", f"${m['aov']:,.2f}")

st.divider()
st.subheader("Results")
with st.expander("Show table", expanded=True):
    st.dataframe(df, use_container_width=True)
