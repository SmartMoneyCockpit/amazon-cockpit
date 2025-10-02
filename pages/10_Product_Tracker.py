
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
import os

st.set_page_config(page_title="Product Tracker", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📦 Product Tracker")
st.caption("Shows sessions, CVR, units, inventory & reviews. If your Google Sheet is empty, this page now falls back to a small sample so it's never blank.")

SB = None
try:
    from utils import sheets_bridge as SB  # expects read_tab(name), write_tab(name, df)
except Exception:
    SB = None

def read_tab(name: str) -> pd.DataFrame:
    if SB is not None:
        try:
            return SB.read_tab(name)
        except Exception:
            pass
    return pd.DataFrame()

def load_sample() -> pd.DataFrame:
    # Attempt to read packaged CSV; otherwise construct inline
    try:
        import pkgutil, io
        # When bundled with app, the path below is available
        path = os.path.join("assets","templates","inventory_sample.csv")
        if os.path.exists(path):
            return pd.read_csv(path)
    except Exception:
        pass
    # Inline fallback
    return pd.DataFrame([
        {"sku":"NOPAL-120","asin":"B00NOPAL01","title":"Nopal Cactus 120ct","inventory":420,"price":24.95,"stars":4.6,"reviews":812,"sessions":1500,"cvr%":6.2,"days of cover":28},
        {"sku":"MANGO-120","asin":"B00MANGO01","title":"Mangosteen Pericarp 120ct","inventory":180,"price":29.95,"stars":4.4,"reviews":365,"sessions":900,"cvr%":4.9,"days of cover":19},
        {"sku":"NOPAL-240","asin":"B00NOPAL02","title":"Nopal Cactus 240ct","inventory":95,"price":39.95,"stars":4.5,"reviews":145,"sessions":600,"cvr%":5.1,"days of cover":12},
    ])

# Try Google Sheets first
inv = read_tab("inventory")
tracker = read_tab("product_tracker")
cat = read_tab("catalog_cache")

# Normalize
for df in [inv, tracker, cat]:
    try:
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception:
        pass

# Determine base
if tracker.empty and inv.empty:
    base = load_sample()
else:
    base = tracker.copy() if not tracker.empty else inv.copy()

# Optional join to inventory if tracker present
if not tracker.empty and not inv.empty and "sku" in inv.columns:
    inv_cols = [c for c in inv.columns if c not in ("sku","asin")]
    base = base.merge(inv[["sku","asin"] + inv_cols] if "asin" in inv.columns else inv[["sku"] + inv_cols],
                      on="sku", how="left")

# Enrich from catalog cache
if not base.empty and not cat.empty and "asin" in base.columns and "asin" in cat.columns:
    keep = ["asin"] + [c for c in ["title","brand","category","weight_kg","size"] if c in cat.columns]
    catv = cat[keep].drop_duplicates("asin")
    base = base.merge(catv, on="asin", how="left")

# Filters
c1, c2 = st.columns(2)
sku_q = c1.text_input("SKU contains", "")
asin_q = c2.text_input("ASIN contains", "")
dfv = base.copy()
if not dfv.empty:
    if "sku" in dfv.columns and sku_q:
        dfv = dfv[dfv["sku"].astype(str).str.contains(sku_q, case=False, na=False)]
    if "asin" in dfv.columns and asin_q:
        dfv = dfv[dfv["asin"].astype(str).str.contains(asin_q, case=False, na=False)]

st.subheader("Tracked Products")
if dfv.empty:
    st.info("No rows found. You're seeing the empty view—use the **Catalog Enrichment** page and populate your Google Sheet tabs (`inventory` or `product_tracker`), or use the sample template below.")
else:
    st.dataframe(dfv, use_container_width=True, hide_index=True)

# KPIs
def numcol(name):
    return pd.to_numeric(dfv.get(name), errors="coerce").fillna(0) if name in dfv.columns else pd.Series(dtype=float)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sessions", f"{int(numcol('sessions').sum()):,}" if not dfv.empty else "—")
k2.metric("Avg CVR", f"{numcol('cvr%').mean():.1f}%" if not dfv.empty and 'cvr%' in dfv.columns else "—")
k3.metric("Avg Stars", f"{numcol('stars').mean():.2f}" if not dfv.empty and 'stars' in dfv.columns else "—")
doc_col = next((c for c in dfv.columns if c.lower()=='days of cover'), None)
k4.metric("At Risk (<10 DoC)",
          f\"{int((pd.to_numeric(dfv[doc_col], errors='coerce').fillna(999) < 10).sum())}\" if doc_col and not dfv.empty else "—")

# Export
st.subheader("Export")
c_csv, c_xlsx = st.columns(2)
c_csv.download_button("CSV", data=dfv.to_csv(index=False).encode("utf-8"), file_name="product_tracker.csv", mime="text/csv")
try:
    import io
    buf = io.BytesIO()
    dfv.to_excel(buf, index=False)
    c_xlsx.download_button("XLSX", data=buf.getvalue(), file_name="product_tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
except Exception:
    pass

st.divider()
st.caption("Need data? Paste this template into your Google Sheet **inventory** tab:")
st.download_button("⬇️ Download inventory_sample.csv", data=pd.DataFrame([
    {"sku":"NOPAL-120","asin":"B00NOPAL01","title":"Nopal Cactus 120ct","inventory":420,"price":24.95,"stars":4.6,"reviews":812,"sessions":1500,"cvr%":6.2,"days of cover":28},
    {"sku":"MANGO-120","asin":"B00MANGO01","title":"Mangosteen Pericarp 120ct","inventory":180,"price":29.95,"stars":4.4,"reviews":365,"sessions":900,"cvr%":4.9,"days of cover":19},
    {"sku":"NOPAL-240","asin":"B00NOPAL02","title":"Nopal Cactus 240ct","inventory":95,"price":39.95,"stars":4.5,"reviews":145,"sessions":600,"cvr%":5.1,"days of cover":12},
]).to_csv(index=False).encode("utf-8"), file_name="inventory_sample.csv", mime="text/csv")
