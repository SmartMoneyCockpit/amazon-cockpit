
import streamlit as st
import pandas as pd

st.set_page_config(page_title="A+ & SEO Panel", layout="wide")
st.title("🧩 A+ & SEO Panel")
st.caption("Keyword indexing health + competitor snapshot. Uses Google Sheets tabs **keywords** and **competitors** (CSV fallback).")

SB = None
try:
    from utils import sheets_bridge as SB  # type: ignore
except Exception:
    SB = None

def read_tab(name: str) -> pd.DataFrame:
    if SB is not None:
        try:
            return SB.read_tab(name)
        except Exception:
            pass
    up = st.file_uploader(f"Upload {name}.csv", type=["csv"], key=f"up_{name}")
    if up:
        return pd.read_csv(up)
    return pd.DataFrame()

# --- Keyword indexing ---
st.header("Keyword Indexing")
kws = read_tab("keywords")
if kws.empty:
    st.info("Add a **keywords** tab with: keyword, priority (High/Med/Low), est_search_volume (opt), indexed (TRUE/FALSE), rank (opt).")
else:
    kws.columns = [c.strip().lower() for c in kws.columns]
    base = kws.copy()
    for col in ["keyword","priority"]:
        if col not in base.columns:
            st.error("Missing columns in keywords tab: keyword, priority")
            st.stop()
    if "indexed" not in base.columns:
        base["indexed"] = ""

    prioritized = base[base["priority"].astype(str).str.lower().isin(["high","med","medium"])]
    total = len(prioritized)
    cov = (prioritized["indexed"].astype(str).str.upper().eq("TRUE")).mean() * 100 if total else 0

    c1,c2,c3 = st.columns(3)
    c1.metric("Tracked Keywords", f"{len(base)}")
    c2.metric("Indexed", f"{int(round(total*cov/100.0))}")
    c3.metric("Not Indexed", f"{max(total - int(round(total*cov/100.0)), 0)}")

    st.dataframe(base, use_container_width=True, hide_index=True)

    missing = prioritized[~prioritized["indexed"].astype(str).str.upper().eq("TRUE")]
    if not missing.empty:
        st.warning(f"{len(missing)} high-priority keyword(s) are NOT indexed.")
        st.dataframe(missing[["keyword","priority"] + (["rank"] if "rank" in missing.columns else [])],
                     use_container_width=True, hide_index=True)
        st.download_button("⬇️ Export (Keywords)", data=base.to_csv(index=False).encode("utf-8"),
                           file_name="keywords_export.csv", mime="text/csv")

# --- Competitor snapshot ---
st.header("Competitor Snapshot")
comps = read_tab("competitors")
if comps.empty:
    st.info("Add a **competitors** tab with: asin,title,brand,price,reviews,stars,weight_kg,size,restricted,notes")
else:
    comps.columns = [c.strip().lower() for c in comps.columns]
    show_cols = [c for c in ["asin","title","price","stars","reviews","a+","mainimagequality"] if c in comps.columns]
    st.dataframe(comps[show_cols] if show_cols else comps, use_container_width=True, hide_index=True)

    # Simple KPIs
    try:
        avg_price = pd.to_numeric(comps.get("price"), errors="coerce").mean()
    except Exception:
        avg_price = None
    try:
        avg_stars = pd.to_numeric(comps.get("stars"), errors="coerce").mean()
    except Exception:
        avg_stars = None
    with_aplus = int(comps.get("a+", pd.Series([False]*len(comps))).astype(bool).sum()) if "a+" in comps.columns else None

    c1,c2,c3 = st.columns(3)
    c1.metric("Avg Price", f"${avg_price:,.2f}" if avg_price is not None else "—")
    c2.metric("Avg Stars", f"{avg_stars:.2f}" if avg_stars is not None else "—")
    c3.metric("With A+ Content", f"{with_aplus}" if with_aplus is not None else "—")

    st.download_button("⬇️ Export (Competitors)",
                       data=comps.to_csv(index=False).encode("utf-8"),
                       file_name="competitors_export.csv",
                       mime="text/csv")

st.caption("Secrets supported: **SHEETS_DOC_ID** + **SHEETS_CREDENTIALS_JSON** via utils.sheets_bridge. If missing, upload CSVs above.")
