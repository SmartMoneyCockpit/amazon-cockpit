
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.auth import gate
import utils.security as sec

from utils.home_metrics import read_tab, derive_finance, count_severity

st.set_page_config(page_title="Home — Global Overview", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("🏠 Global Overview")
st.caption("Your cockpit home: Finance health, Actions, Inventory risk, Compliance, and quick links.")

# ---- Pull data ----
fin = derive_finance(read_tab("profitability_monthly"))
actions = read_tab("actions_out")
lowdoc = read_tab("alerts_out_low_doc")
compliance = read_tab("alerts_out_compliance")

for df in [actions, lowdoc, compliance]:
    try: df.columns = [c.strip().lower() for c in df.columns]
    except Exception: pass

# ---- Time context ----
today = pd.Timestamp.utcnow().tz_localize("UTC").tz_convert("America/Mazatlan")
this_month = today.strftime("%Y-%m")
this_year = today.year

# ---- Finance KPIs ----
rev_mtd = net_mtd = rev_ytd = net_ytd = 0.0
if not fin.empty:
    mtd = fin[fin["month"] == this_month]
    ytd = fin[pd.to_datetime(fin["month"], errors="coerce").dt.year == this_year]
    rev_mtd = float(mtd["revenue"].sum())
    net_mtd = float(mtd["net"].sum())
    rev_ytd = float(ytd["revenue"].sum())
    net_ytd = float(ytd["net"].sum())

# ---- Action counts ----
crit, attn, green = count_severity(actions)
doc_at_risk = len(lowdoc) if isinstance(lowdoc, pd.DataFrame) and not lowdoc.empty else 0
comp_due = len(compliance) if isinstance(compliance, pd.DataFrame) and not compliance.empty else 0

# ---- KPI tiles ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue (MTD)", f"${rev_mtd:,.2f}")
c2.metric("Net (MTD)", f"${net_mtd:,.2f}")
c3.metric("Critical Actions", f"{crit}")
c4.metric("Low DoC SKUs", f"{doc_at_risk}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Revenue (YTD)", f"${rev_ytd:,.2f}")
c6.metric("Net (YTD)", f"${net_ytd:,.2f}")
c7.metric("Attention Items", f"{attn}")
c8.metric("Compliance Due", f"{comp_due}")

st.divider()

# ---- Compact charts ----
st.subheader("Trends")
colA, colB = st.columns(2)

with colA:
    if not fin.empty and "month" in fin.columns:
        trend = fin.groupby("month", as_index=False).agg(revenue=("revenue","sum"), net=("net","sum"))
        trend["month_dt"] = pd.to_datetime(trend["month"], errors="coerce")
        trend = trend.sort_values("month_dt").tail(6)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(trend["month_dt"].dt.strftime("%Y-%m"), trend["revenue"])
        ax.set_title("Revenue (last 6 months)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig)
    else:
        st.info("No profitability data yet.")

with colB:
    if not actions.empty:
        # Bar of action counts by type (top 5)
        g = actions.copy()
        g["type"] = g.get("type","unknown")
        bar = g.groupby("type").size().sort_values(ascending=False).head(5)
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.bar(bar.index.astype(str), bar.values)
        ax2.set_title("Top Action Types")
        ax2.set_ylabel("Count")
        plt.xticks(rotation=20, ha="right")
        st.pyplot(fig2)
    else:
        st.info("No actions yet.")

# ---- Latest actions (compact) ----
st.subheader("Latest Actions")
if not actions.empty:
    # Red first, then yellow
    if "severity" in actions.columns:
        sev = pd.Categorical(actions["severity"].astype(str), categories=["red","yellow","green"], ordered=True)
        actions = actions.assign(_sev=sev).sort_values(["_sev"]).drop(columns=["_sev"])
    st.dataframe(actions.head(15), use_container_width=True, hide_index=True)
else:
    st.info("All clear.")

# ---- Quick links ----
st.subheader("Quick Links")
st.markdown(
    "- **📊 Finance Dashboard v2**  \n"
    "- **📊 Finance Heatmap**  \n"
    "- **🧭 Trade / Action Hub**  \n"
    "- **🚨 Alerts Center**  \n"
    "- **🔄 Data Sync**"
)
st.caption("Tip: The Overview uses your Google Sheet tabs. Seed data if this is a fresh environment.")
