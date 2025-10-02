
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Product Research", layout="wide")
st.title("🧪 Product Research — Opportunity Scoring")
st.caption("Ranks opportunities using your **competitors** and **keywords** tabs. No scraping; sheet/CSV only.")

SB = None
try:
    from utils import sheets_bridge as SB  # type: ignore
except Exception:
    SB = None

def read_tab_or_upload(name):
    if SB is not None:
        try:
            return SB.read_tab(name)
        except Exception:
            pass
    up = st.file_uploader(f"Upload {name}.csv", type=["csv"], key=f"up_{name}")
    if up:
        return pd.read_csv(up)
    return pd.DataFrame()

comps = read_tab_or_upload("competitors")
kws = read_tab_or_upload("keywords")

if comps.empty:
    st.info("Add a **competitors** tab with columns: asin,title,brand,price,reviews,stars,weight_kg,size,restricted,notes")
    st.stop()

comps.columns = [c.strip().lower() for c in comps.columns]
kws.columns = [c.strip().lower() for c in kws.columns]

# Sidebar weights
st.sidebar.header("Weights (0–10)")
w_price = st.sidebar.slider("Lower price advantage", 0.0, 10.0, 4.0, 0.5)
w_reviews = st.sidebar.slider("Low reviews advantage", 0.0, 10.0, 3.0, 0.5)
w_stars = st.sidebar.slider("High stars advantage", 0.0, 10.0, 3.0, 0.5)
w_weight = st.sidebar.slider("Lower weight advantage", 0.0, 10.0, 2.0, 0.5)
w_restricted = st.sidebar.slider("Unrestricted bonus", 0.0, 10.0, 5.0, 0.5)
w_kw = st.sidebar.slider("Keyword priority coverage", 0.0, 10.0, 5.0, 0.5)

# Compute normalized features
df = comps.copy()
for col in ["price","reviews","stars","weight_kg"]:
    if col not in df.columns: df[col] = np.nan

# Normalize where higher is better; for price/reviews/weight lower is better
def norm_lower_better(x):
    x = x.astype(float)
    return 1 - (x - x.min()) / max((x.max() - x.min()), 1e-9)

def norm_higher_better(x):
    x = x.astype(float)
    return (x - x.min()) / max((x.max() - x.min()), 1e-9)

df["_n_price"] = norm_lower_better(df["price"]) if df["price"].notna().any() else 0
df["_n_reviews"] = norm_lower_better(df["reviews"]) if df["reviews"].notna().any() else 0
df["_n_stars"] = norm_higher_better(df["stars"]) if df["stars"].notna().any() else 0
df["_n_weight"] = norm_lower_better(df["weight_kg"]) if df["weight_kg"].notna().any() else 0

# Restricted bonus
if "restricted" in df.columns:
    df["_restricted_bonus"] = df["restricted"].astype(str).str.upper().map({"TRUE":0,"YES":0}).fillna(1.0)
else:
    df["_restricted_bonus"] = 1.0

# Keyword coverage from kws
kw_score = 1.0
if not kws.empty and "priority" in kws.columns:
    prioritized = kws[kws["priority"].astype(str).str.lower().isin(["high","med","medium"])]
    total = max(len(prioritized), 1)
    # if 'indexed' exists, reward indexed ones
    if "indexed" in prioritized.columns:
        cov = (prioritized["indexed"].astype(str).str.upper().eq("TRUE")).mean()
        kw_score = cov
    else:
        kw_score = 0.5  # neutral if unknown

df["opportunity_score"] = (
    w_price * df["_n_price"] +
    w_reviews * df["_n_reviews"] +
    w_stars * df["_n_stars"] +
    w_weight * df["_n_weight"] +
    w_restricted * df["_restricted_bonus"] +
    w_kw * kw_score
)

df = df.sort_values("opportunity_score", ascending=False)
st.subheader("Ranked Opportunities")
st.dataframe(df.drop(columns=[c for c in df.columns if c.startswith("_n_") or c=="_restricted_bonus"]),
             use_container_width=True, hide_index=True)

st.download_button("⬇️ Export Ranked List (CSV)",
                   data=df.to_csv(index=False).encode("utf-8"),
                   file_name="product_research_ranked.csv",
                   mime="text/csv")
