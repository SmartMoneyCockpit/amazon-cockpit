import streamlit as st
import pandas as pd
from infra.sheets_client import SheetsClient
from utils.catalog_tools import demo_catalog, normalize, validation_badges

st.set_page_config(page_title="Catalog Enrichment", layout="wide")
st.title("Catalog Enrichment")

@st.cache_data(show_spinner=False, ttl=300)
def _read_catalog():
    try:
        sc = SheetsClient()
        rows = sc.read_table("Catalog")
        return normalize(pd.DataFrame(rows))
    except Exception:
        return normalize(demo_catalog())

d = _read_catalog()
v = validation_badges(d)

# Summary counts
c1, c2, c3 = st.columns(3)
c1.metric("Title OK (≥60 chars)", int(v["title_ok"].sum()))
c2.metric("Description OK", int(v["desc_ok"].sum()))
c3.metric("Price OK (>0)", int(v["price_ok"].sum()))

st.divider()
st.subheader("Validation Badges")

def _badge(ok: bool, label: str):
    color = "#16a34a" if ok else "#ef4444"
    return f"<span style='padding:.15rem .5rem;border-radius:999px;background:{color};color:#fff;font-size:.75rem;'>{label}</span>"

# Build a compact table with badges
show = v.copy()
show["Title Badge"] = show["title_ok"].apply(lambda x: _badge(bool(x), "OK") if x else _badge(False, "Short"))
show["Desc Badge"]  = show["desc_ok"].apply(lambda x: _badge(bool(x), "OK") if x else _badge(False, "Missing"))
show["Price Badge"] = show["price_ok"].apply(lambda x: _badge(bool(x), "OK") if x else _badge(False, "Invalid"))

cols = ["asin","sku","title","price","Title Badge","Desc Badge","Price Badge"]
st.write("")
st.caption("Badges are visual only; export corrected CSV when ready.")

with st.expander("Show table", expanded=True):
    st.dataframe(show[cols], use_container_width=True, hide_index=True)

# Export corrected CSV
st.divider()
if st.button("Export Corrected CSV"):
    csv = v.to_csv(index=False).encode("utf-8")
    st.download_button("Download", data=csv, file_name="catalog_validated.csv", mime="text/csv")
