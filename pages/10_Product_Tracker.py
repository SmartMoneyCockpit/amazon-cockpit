
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

st.set_page_config(page_title="Product Tracker", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📦 Product Tracker")
st.caption("Sessions, CVR, units, inventory & reviews — now enriched with **catalog_cache** (title/brand/category).")

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

# --- Load base dataset ---
# Prefer your existing Sheet tabs if present; otherwise show sample data so the page is never blank.
inv = read_tab("inventory")
tracker = read_tab("product_tracker")  # optional tab if you keep sessions/CTR etc there
cat = read_tab("catalog_cache")

# Normalize
for df in [inv, tracker, cat]:
    try:
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception:
        pass

# If you don't have a consolidated tracker sheet, build a basic view from inventory only
if tracker.empty:
    base = inv.copy()
else:
    # If both exist, prefer the richer "tracker" data and left-join inventory counts
    base = tracker.copy()
    if not inv.empty and "sku" in inv.columns:
        inv_cols = [c for c in inv.columns if c not in ("sku","asin")]
        base = base.merge(inv[["sku","asin"] + inv_cols] if "asin" in inv.columns else inv[["sku"] + inv_cols],
                          on="sku", how="left")

# --- Filters ---
c1, c2 = st.columns(2)
sku_q = c1.text_input("SKU contains", "")
asin_q = c2.text_input("ASIN contains", "")

dfv = base.copy()
if not dfv.empty:
    if "sku" in dfv.columns and sku_q:
        dfv = dfv[dfv["sku"].astype(str).str.contains(sku_q, case=False, na=False)]
    if "asin" in dfv.columns and asin_q:
        dfv = dfv[dfv["asin"].astype(str).str.contains(asin_q, case=False, na=False)]

# --- Join with catalog cache for title/brand/category ---
if not dfv.empty and not cat.empty and "asin" in dfv.columns and "asin" in cat.columns:
    keep = ["asin"] + [c for c in ["title","brand","category","weight_kg","size"] if c in cat.columns]
    catv = cat[keep].drop_duplicates("asin")
    dfv = dfv.merge(catv, on="asin", how="left")

# --- Display table ---
st.subheader("Tracked Products")
st.dataframe(dfv, use_container_width=True, hide_index=True)

# --- KPIs (best-effort) ---
def to_num(s, default=0.0):
    try: return float(s)
    except: return default

k1, k2, k3, k4 = st.columns(4)
# Sessions & CVR if present
if "sessions" in dfv.columns:
    k1.metric("Total Sessions", f"{int(pd.to_numeric(dfv['sessions'], errors='coerce').fillna(0).sum()):,}")
else:
    k1.metric("Total Sessions", "—")
if "cvr%" in [c.lower() for c in dfv.columns]:
    col = [c for c in dfv.columns if c.lower()=="cvr%"][0]
    k2.metric("Avg CVR", f"{pd.to_numeric(dfv[col], errors='coerce').mean():.1f}%")
else:
    k2.metric("Avg CVR", "—")
if "stars" in dfv.columns:
    k3.metric("Avg Stars", f"{pd.to_numeric(dfv['stars'], errors='coerce').mean():.2f}")
else:
    k3.metric("Avg Stars", "—")
if "inventory" in dfv.columns and "days of cover" in [c.lower() for c in dfv.columns]:
    doc_col = [c for c in dfv.columns if c.lower()=="days of cover"][0]
    low_doc = int((pd.to_numeric(dfv[doc_col], errors='coerce').fillna(999) < 10).sum())
    k4.metric("At Risk (<10 DoC)", f"{low_doc}")
else:
    k4.metric("At Risk (<10 DoC)", "—")

# --- Export buttons ---
st.subheader("Export")
c_csv, c_xlsx = st.columns(2)
c_csv.download_button("CSV", data=dfv.to_csv(index=False).encode("utf-8"), file_name="product_tracker.csv", mime="text/csv")
try:
    import io
    import pandas as pd
    buf = io.BytesIO()
    dfv.to_excel(buf, index=False)
    c_xlsx.download_button("XLSX", data=buf.getvalue(), file_name="product_tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
except Exception:
    pass

# --- Refresh Catalog button (visible ASINs) ---
visible_asins = sorted(dfv.get("asin", pd.Series([], dtype=str)).dropna().astype(str).unique().tolist()) if not dfv.empty else []
if visible_asins:
    st.caption(f"Visible unique ASINs: {len(visible_asins)}")
    if st.button("🚀 Refresh catalog for visible ASINs → update `catalog_cache`"):
        try:
            from integrations.catalog import enrich_asins
            df_new = enrich_asins(visible_asins)
            if df_new is not None and not df_new.empty:
                cache = read_tab("catalog_cache")
                cache = cache if isinstance(cache, pd.DataFrame) else pd.DataFrame()
                # normalize
                for df in [cache, df_new]:
                    try: df.columns = [c.strip().lower() for c in df.columns]
                    except: pass
                # upsert by asin
                if not cache.empty and "asin" in cache.columns:
                    cols = list({*cache.columns, *df_new.columns})
                    cache = cache.set_index("asin")
                    df_new = df_new.set_index("asin")
                    cache.update(df_new)
                    out = cache.reset_index()[cols]
                else:
                    out = df_new.reset_index(drop=True)
                res = write_tab("catalog_cache", out, clear=True)
                st.success(f"Catalog cache updated: {res}")
                st.experimental_rerun()
            else:
                st.warning("No data returned from enrichment (library/creds/API).")
        except Exception as e:
            st.error(f"Failed to refresh catalog: {e}")
