
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="PPC Import (CSV/Sheet) — Ads-free", layout="wide")
st.title("📥 PPC Import (CSV/Sheet) — Ads-free")
st.caption("Import Sponsored Products CSV or read the 'ppc_import' tab from your Google Sheet. "
           "This page **does not** call the Amazon Ads API. It provides KPI summaries and a Negative Keyword suggestion export.")

# Optional Sheets bridge
SB = None
try:
    from utils import sheets_bridge as SB  # type: ignore
except Exception:
    SB = None

# Helpers
def kpi(df: pd.DataFrame):
    df = df.copy()
    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    # Expected columns (any naming variants handled loosely)
    col_map = {
        "impressions": ["impressions", "impr"],
        "clicks": ["clicks"],
        "spend": ["spend", "cost"],
        "orders": ["orders", "purchases", "conversions"],
        "sales": ["sales", "revenue"],
    }
    def pick(name):
        for cand in col_map[name]:
            if cand in df.columns: return cand
        return None

    impr = pick("impressions")
    clk = pick("clicks")
    spend = pick("spend")
    orders = pick("orders")
    sales = pick("sales")

    totals = {}
    if impr and clk:
        totals["CTR"] = round((df[clk].sum() / max(df[impr].sum(), 1)) * 100, 2)
    if spend and clk:
        totals["CPC"] = round((df[spend].sum() / max(df[clk].sum(), 1)), 4)
    if spend and sales:
        totals["ACOS"] = round((df[spend].sum() / max(df[sales].sum(), 1)) * 100, 2)
    if orders:
        totals["Orders"] = int(df[orders].sum())
    if sales:
        totals["Sales"] = float(df[sales].sum())
    if spend:
        totals["Spend"] = float(df[spend].sum())
    return totals

def suggest_negatives(df: pd.DataFrame, acos_target: float = 30.0, min_spend: float = 5.0, min_clicks: int = 8):
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    # determine columns
    kw_col = None
    for cand in ["keyword", "search term", "search_term"]:
        if cand in df.columns:
            kw_col = cand; break
    if kw_col is None:
        return pd.DataFrame(columns=["keyword","reason"])

    spend = df.get("spend") or df.get("cost")
    clicks = df.get("clicks")
    orders = df.get("orders") or df.get("purchases") or df.get("conversions")
    sales = df.get("sales") or df.get("revenue")

    reasons = []
    # zero-order spenders
    if spend is not None and orders is not None:
        cond = (df[orders].fillna(0) == 0) & (df[spend].fillna(0) >= min_spend)
        reasons.append(pd.DataFrame({"keyword": df.loc[cond, kw_col], "reason": "Spend >= ${} with 0 orders".format(min_spend)}))
    # high ACOS
    if spend is not None and sales is not None:
        acos = (df[spend].fillna(0) / df[sales].replace(0, pd.NA)).astype(float) * 100
        cond = acos.fillna(9999) > acos_target
        reasons.append(pd.DataFrame({"keyword": df.loc[cond, kw_col], "reason": f"ACOS > {acos_target}%"}))
    # high clicks, no orders
    if clicks is not None and orders is not None:
        cond = (df[clicks].fillna(0) >= min_clicks) & (df[orders].fillna(0) == 0)
        reasons.append(pd.DataFrame({"keyword": df.loc[cond, kw_col], "reason": f"Clicks >= {min_clicks} with 0 orders"}))

    if not reasons:
        return pd.DataFrame(columns=["keyword","reason"])
    out = pd.concat(reasons, ignore_index=True).dropna()
    out = out.drop_duplicates().sort_values("keyword")
    return out

# Sidebar
st.sidebar.header("Data Source")
src = st.sidebar.radio("Choose", ["Upload CSV", "Google Sheet tab: ppc_import"])
acos_target = st.sidebar.slider("Target ACOS %", 5.0, 60.0, 30.0, 0.5)
min_spend = st.sidebar.number_input("Min spend for negatives ($)", 0.0, 1000.0, 5.0, 0.5)
min_clicks = st.sidebar.number_input("Min clicks (no orders)", 0, 1000, 8, 1)

df = pd.DataFrame()
if src == "Upload CSV":
    uploaded = st.file_uploader("Drop a PPC CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
else:
    if SB is None:
        st.warning("Sheets bridge not found. Ensure `utils/sheets_bridge.py` exists. Falling back to CSV upload.")
    else:
        try:
            df = SB.read_tab("ppc_import")
        except Exception as e:
            st.error(f"Couldn't read 'ppc_import' tab from Google Sheets: {e}")

if df.empty:
    st.info("Load a dataset to see KPIs and suggestions.")
    st.stop()

st.subheader("KPI Summary")
metrics = kpi(df)
cols = st.columns(len(metrics) or 1)
for i, (k, v) in enumerate(metrics.items()):
    cols[i].metric(k, f"{v:,.2f}" if isinstance(v, float) else v)

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Suggested Negative Keywords")
negs = suggest_negatives(df, acos_target=acos_target, min_spend=min_spend, min_clicks=min_clicks)
st.dataframe(negs, use_container_width=True, hide_index=True)
if not negs.empty:
    st.download_button("⬇️ Download Negatives (CSV)",
                       data=negs.to_csv(index=False).encode("utf-8"),
                       file_name="ppc_negative_suggestions.csv",
                       mime="text/csv")
st.caption("Tip: You can paste these into your bulk negative uploads or keep a 'negatives' tab in your Sheet.")
