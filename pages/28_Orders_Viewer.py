
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Orders Viewer", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📦 Orders Viewer")

def read_orders() -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        return SB.read_tab("orders")
    except Exception:
        return pd.DataFrame(columns=["order_id","purchase_date","status","sku","asin","qty","price"])

df = read_orders()
if df.empty:
    st.info("No orders yet. Run **Data Sync** first.")
    st.stop()

# Normalize and parse date
df.columns = [c.strip().lower() for c in df.columns]
if "purchase_date" in df.columns:
    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")

c1, c2, c3 = st.columns(3)
days = c1.slider("Days back", 7, 90, 30, 1)
sku_q = c2.text_input("SKU contains", "")
asin_q = c3.text_input("ASIN contains", "")

since = pd.Timestamp.utcnow() - pd.Timedelta(days=days)
flt = df.copy()
if "purchase_date" in flt.columns:
    flt = flt[flt["purchase_date"] >= since]
if sku_q:
    flt = flt[flt["sku"].astype(str).str.contains(sku_q, case=False, na=False)]
if asin_q:
    flt = flt[flt["asin"].astype(str).str.contains(asin_q, case=False, na=False)]

st.subheader("Results")
st.dataframe(flt, use_container_width=True, hide_index=True)

st.download_button("⬇️ Download CSV", data=flt.to_csv(index=False).encode("utf-8"),
                   file_name="orders_view.csv", mime="text/csv")
