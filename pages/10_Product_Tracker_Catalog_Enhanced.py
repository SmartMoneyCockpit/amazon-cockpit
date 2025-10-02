
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Product Tracker (Catalog Enhanced)", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📦 Product Tracker — Catalog Enhanced")
st.caption("Joins your Inventory with `catalog_cache` (title/brand/category) and lets you refresh catalog data for the currently visible ASINs.")

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

def write_tab(name: str, df: pd.DataFrame, clear: bool = True) -> str:
    if SB is not None and hasattr(SB, "write_tab"):
        try:
            SB.write_tab(name, df, clear=clear)
            return f"sheet:{name}:{len(df)}"
        except Exception as e:
            return f"error:{e}"
    return "no_sheets_bridge"

# Load base (inventory) and catalog cache
inv = read_tab("inventory")
cat = read_tab("catalog_cache")

inv.columns = [c.strip().lower() for c in inv.columns]
cat.columns = [c.strip().lower() for c in cat.columns]

if inv.empty:
    st.info("No `inventory` tab found or it is empty. Run **Data Sync** first.")
    st.stop()

# Filters
c1, c2 = st.columns(2)
sku_q = c1.text_input("SKU contains", "")
asin_q = c2.text_input("ASIN contains", "")

base = inv.copy()
if sku_q:
    base = base[base["sku"].astype(str).str.contains(sku_q, case=False, na=False)]
if asin_q and "asin" in base.columns:
    base = base[base["asin"].astype(str).str.contains(asin_q, case=False, na=False)]

# Join with catalog cache
if not cat.empty and "asin" in cat.columns:
    join_cols = ["asin"] + [c for c in ["title","brand","category","weight_kg","size"] if c in cat.columns]
    show_cat = cat[join_cols].drop_duplicates("asin")
    merged = base.merge(show_cat, on="asin", how="left")
else:
    merged = base.copy()

st.subheader("Inventory × Catalog")
st.dataframe(merged, use_container_width=True, hide_index=True)

# Refresh button for visible ASINs
asins = sorted(merged.get("asin", pd.Series([], dtype=str)).dropna().astype(str).unique().tolist())
if asins:
    st.caption(f"Visible unique ASINs: {len(asins)}")
    if st.button("🚀 Refresh catalog for visible ASINs → update `catalog_cache`"):
        try:
            from integrations.catalog import enrich_asins
            df = enrich_asins(asins)
            if df is not None and not df.empty:
                # Append/merge into existing cache
                cache = read_tab("catalog_cache")
                cache = cache if isinstance(cache, pd.DataFrame) else pd.DataFrame()
                cache.columns = [c.strip().lower() for c in cache.columns]
                df.columns = [c.strip().lower() for c in df.columns]
                if not cache.empty and "asin" in cache.columns:
                    # upsert by asin
                    keep_cols = list({*cache.columns, *df.columns})
                    cache = cache.set_index("asin")
                    df = df.set_index("asin")
                    cache.update(df)
                    out = cache.reset_index()[keep_cols]
                else:
                    out = df.reset_index(drop=True)
                res = write_tab("catalog_cache", out, clear=True)
                st.success(f"Catalog cache updated: {res}")
                st.experimental_rerun()
            else:
                st.warning("No data returned from enrichment (library/creds/API).")
        except Exception as e:
            st.error(f"Failed to refresh catalog: {e}")
else:
    st.info("No ASINs in the current view to enrich.")
