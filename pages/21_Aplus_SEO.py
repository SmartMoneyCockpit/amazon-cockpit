
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="A+ & SEO Indexing Checker", layout="wide")
st.title("🧩 A+ & SEO Indexing Checker")
st.caption("No scraping. Uses your **keywords** tab flags. Focus is on coverage tracking and action lists.")

SB = None
try:
    from utils import sheets_bridge as SB  # type: ignore
except Exception:
    SB = None

def load_keywords():
    if SB is not None:
        try:
            df = SB.read_tab("keywords")
            return df
        except Exception as e:
            st.error(f"Couldn't read 'keywords' tab: {e}")
    uploaded = st.file_uploader("Or upload keywords CSV", type=["csv"])
    if uploaded:
        return pd.read_csv(uploaded)
    return pd.DataFrame()

df = load_keywords()
if df.empty:
    st.info("Add a 'keywords' tab with columns: keyword, priority (High/Med/Low), est_search_volume, indexed (TRUE/FALSE/blank).")
    st.stop()

df.columns = [c.strip().lower() for c in df.columns]
for col in ["keyword", "priority"]:
    if col not in df.columns:
        st.error("Missing columns. Need at least: keyword, priority.")
        st.stop()

if "indexed" not in df.columns:
    df["indexed"] = ""

prioritized = df[df["priority"].str.lower().isin(["high","med","medium"])]
cov = 0
total = len(prioritized)
if total > 0:
    cov = (prioritized["indexed"].astype(str).str.upper().eq("TRUE")).mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Prioritized keywords", f"{total}")
c2.metric("Indexed coverage", f"{cov:.1f}%")
c3.metric("Missing", f"{max(total - int(round(cov/100*total)), 0)}")

st.subheader("Not Indexed (Prioritized)")
missing = prioritized[~prioritized["indexed"].astype(str).str.upper().eq("TRUE")]
st.dataframe(missing[["keyword","priority"] + [c for c in ["est_search_volume"] if c in missing.columns]],
             use_container_width=True, hide_index=True)

if not missing.empty:
    csv = missing[["keyword","priority"]].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export Missing Indexing (CSV)", data=csv, file_name="a_plus_seo_missing.csv", mime="text/csv")

st.subheader("All Keywords")
st.dataframe(df, use_container_width=True, hide_index=True)
