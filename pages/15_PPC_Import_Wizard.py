
import streamlit as st
import pandas as pd
from utils.sheets_writer import write_df
from datetime import datetime, timedelta

st.set_page_config(page_title="PPC Import (CSV/Sheet) — Ads-free", layout="wide")
st.title("📥 PPC Import (CSV/Sheet) — Ads-free")
st.caption("Import a PPC CSV or read the 'ppc_import' tab. Generate KPIs and Negative Keyword suggestions.")

SB = None
try:
    from utils import sheets_bridge as SB
except Exception:
    SB = None

def load_data(src: str):
    if src == "Upload CSV":
        up = st.file_uploader("Drop a PPC CSV", type=["csv"])
        if up: return pd.read_csv(up)
        return pd.DataFrame()
    else:
        if SB is None:
            st.warning("Sheets bridge not found. Falling back to CSV upload.")
            return pd.DataFrame()
        try:
            return SB.read_tab("ppc_import")
        except Exception as e:
            st.error(f"Couldn't read 'ppc_import': {e}")
            return pd.DataFrame()

def kpi(df: pd.DataFrame):
    d = df.copy()
    d.columns = [c.strip().lower() for c in d.columns]
    impr = d.get("impressions") or d.get("impr")
    clk = d.get("clicks")
    spend = d.get("spend") or d.get("cost")
    orders = d.get("orders") or d.get("purchases") or d.get("conversions")
    sales = d.get("sales") or d.get("revenue")
    out = {}
    if impr is not None and clk is not None:
        out["CTR"] = round((clk.sum()/max(impr.sum(),1))*100,2)
    if spend is not None and clk is not None:
        out["CPC"] = round((spend.sum()/max(clk.sum(),1)),4)
    if spend is not None and sales is not None:
        out["ACOS"] = round((spend.sum()/max(sales.sum(),1))*100,2)
    if orders is not None: out["Orders"] = int(orders.sum())
    if sales is not None: out["Sales"] = float(sales.sum())
    if spend is not None: out["Spend"] = float(spend.sum())
    return out

def suggest_negatives(df: pd.DataFrame, acos_target: float, min_spend: float, min_clicks: int):
    d = df.copy()
    d.columns = [c.strip().lower() for c in d.columns]
    kw_col = None
    for c in ["keyword","search term","search_term","query"]:
        if c in d.columns: kw_col = c; break
    if kw_col is None:
        return pd.DataFrame(columns=["keyword","reason"])
    spend = d.get("spend") or d.get("cost")
    clicks = d.get("clicks")
    orders = d.get("orders") or d.get("purchases") or d.get("conversions")
    sales = d.get("sales") or d.get("revenue")

    out = []
    if spend is not None and orders is not None:
        cond = (orders.fillna(0)==0) & (spend.fillna(0)>=min_spend)
        out.append(pd.DataFrame({"keyword": d.loc[cond, kw_col], "reason": f"Spend ≥ ${min_spend} with 0 orders"}))
    if spend is not None and sales is not None:
        acos = (spend.fillna(0)/d[sales.name].replace(0, pd.NA)).astype(float)*100
        cond = acos.fillna(9999) > acos_target
        out.append(pd.DataFrame({"keyword": d.loc[cond, kw_col], "reason": f"ACOS > {acos_target}"}))
    if clicks is not None and orders is not None:
        cond = (clicks.fillna(0)>=min_clicks) & (orders.fillna(0)==0)
        out.append(pd.DataFrame({"keyword": d.loc[cond, kw_col], "reason": f"Clicks ≥ {min_clicks} with 0 orders"}))
    if not out: return pd.DataFrame(columns=["keyword","reason"])
    res = pd.concat(out, ignore_index=True).drop_duplicates()
    return res.sort_values("keyword")

# Sidebar
st.sidebar.header("Data Source")
src = st.sidebar.radio("Choose", ["Upload CSV","Google Sheet tab: ppc_import"])

st.sidebar.header("Preset")
preset = st.sidebar.selectbox("Suggestion preset", ["Balanced","Aggressive","Conservative"])
if preset == "Aggressive":
    default = dict(acos=25.0, spend=3.0, clicks=6)
elif preset == "Conservative":
    default = dict(acos=40.0, spend=10.0, clicks=12)
else:  # Balanced
    default = dict(acos=30.0, spend=5.0, clicks=8)

acos_target = st.sidebar.slider("Target ACOS %", 5.0, 60.0, float(default["acos"]), 0.5)
min_spend = st.sidebar.number_input("Min spend for negatives ($)", 0.0, 1000.0, float(default["spend"]), 0.5)
min_clicks = st.sidebar.number_input("Min clicks (no orders)", 0, 1000, int(default["clicks"]), 1)

df = load_data(src)
if df.empty:
    st.info("Load a dataset to see KPIs and suggestions.")
    st.stop()

st.subheader("KPI Summary")
metrics = kpi(df)
cols = st.columns(len(metrics) or 1)
for i,(k,v) in enumerate(metrics.items()):
    cols[i].metric(k, f"{v:,.2f}" if isinstance(v,float) else v)

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Suggested Negative Keywords")
negs = suggest_negatives(df, acos_target, min_spend, min_clicks)
st.dataframe(negs, use_container_width=True, hide_index=True)

if not negs.empty:
    st.download_button("⬇️ Download Negatives (CSV)",
                       data=negs.to_csv(index=False).encode("utf-8"),
                       file_name="ppc_negative_suggestions.csv",
                       mime="text/csv")
    if st.button("📤 Save to Google Sheet tab → ppc_negatives"):
        res = write_df("ppc_negatives", negs, clear=False)
        st.success(f"Saved negatives to: {res}")
