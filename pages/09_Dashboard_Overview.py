
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils.auth import gate
import utils.security as sec

# Optional helpers
def read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            return df
    except Exception:
        pass
    return pd.DataFrame()

st.set_page_config(page_title="Dashboard Overview", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("📈 Dashboard Overview")
st.caption("One-glance cockpit: Revenue, Net, Actions, Inventory at risk.")

# ---- Data pulls ----
fin = read_tab("profitability_monthly")
actions = read_tab("actions_out")
lowdoc = read_tab("alerts_out_low_doc")
comp_due = read_tab("alerts_out_compliance")

# Normalize
for df in [fin, actions, lowdoc, comp_due]:
    try: df.columns = [c.strip().lower() for c in df.columns]
    except Exception: pass

# KPI derivations
today = pd.Timestamp.utcnow().tz_localize("UTC").tz_convert("America/Mazatlan")
this_month = today.strftime("%Y-%m")
this_year = today.year

rev_mtd = 0.0; net_mtd = 0.0; rev_ytd = 0.0; net_ytd = 0.0
if not fin.empty:
    if "date" in fin.columns and "month" not in fin.columns:
        fin["month"] = pd.to_datetime(fin["date"], errors="coerce").dt.to_period("M").astype(str)
    fin["revenue"] = pd.to_numeric(fin.get("revenue"), errors="coerce").fillna(0)
    fin["fees"] = pd.to_numeric(fin.get("fees"), errors="coerce").fillna(0)
    fin["other"] = pd.to_numeric(fin.get("other"), errors="coerce").fillna(0)
    fin["net"] = fin["revenue"] - fin["fees"] - fin["other"]
    # Month filters
    mtd = fin[fin["month"] == this_month]
    ytd = fin[pd.to_datetime(fin["month"], errors="coerce").dt.year == this_year]
    rev_mtd = float(mtd["revenue"].sum())
    net_mtd = float(mtd["net"].sum())
    rev_ytd = float(ytd["revenue"].sum())
    net_ytd = float(ytd["net"].sum())

critical = int((actions["severity"].astype(str).str.lower() == "red").sum()) if "severity" in actions.columns else 0
attention = int((actions["severity"].astype(str).str.lower() == "yellow").sum()) if "severity" in actions.columns else 0
doc_at_risk = len(lowdoc) if isinstance(lowdoc, pd.DataFrame) and not lowdoc.empty else 0
comp_expiring = len(comp_due) if isinstance(comp_due, pd.DataFrame) and not comp_due.empty else 0

# ---- KPI tiles ----
k1, k2, k3, k4 = st.columns(4)
k1.metric("Revenue (MTD)", f"${rev_mtd:,.2f}")
k2.metric("Net (MTD)", f"${net_mtd:,.2f}")
k3.metric("Critical Actions", f"{critical}")
k4.metric("Low DoC SKUs", f"{doc_at_risk}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Revenue (YTD)", f"${rev_ytd:,.2f}")
k6.metric("Net (YTD)", f"${net_ytd:,.2f}")
k7.metric("Attention Items", f"{attention}")
k8.metric("Compliance Due", f"{comp_expiring}")

st.divider()

# ---- Revenue trend (last 6 months) ----
st.subheader("Revenue Trend (Last 6 Months)")
if not fin.empty and "month" in fin.columns:
    trend = fin.groupby("month", as_index=False).agg(revenue=("revenue","sum"), net=("net","sum"))
    trend["month_dt"] = pd.to_datetime(trend["month"], errors="coerce")
    trend = trend.sort_values("month_dt").tail(6)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(trend["month_dt"].dt.strftime("%Y-%m"), trend["revenue"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.set_title("Revenue (sum)")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)
else:
    st.info("No profitability data yet. Run Data Sync to populate `profitability_monthly`.")

# ---- Top Actions table ----
st.subheader("Top Actions")
if not actions.empty:
    # Sort: red first, then yellow
    sev = pd.Categorical(actions["severity"].astype(str), categories=["red","yellow","green"], ordered=True) if "severity" in actions.columns else None
    if sev is not None:
        actions = actions.assign(_sev=sev).sort_values(["_sev","type","key"]).drop(columns=["_sev"])
    st.dataframe(actions.head(20), use_container_width=True, hide_index=True)
else:
    st.info("No actions yet. Check Trade / Action Hub.")

# ---- Quick Links ----
st.subheader("Quick Links")
st.caption("Open these pages for details:")
st.markdown("- **📊 Finance Dashboard v2** → monthly breakdown\n- **📊 Finance Heatmap** → margin colors by SKU×Month\n- **🧭 Trade / Action Hub** → unified action list\n- **🚨 Alerts Center** → low DoC / compliance / PPC surge\n- **🔄 Data Sync** → refresh + rollup + sheet writes")

