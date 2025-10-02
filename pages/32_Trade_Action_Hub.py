
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
from utils.alerts import load_thresholds
from utils.actions import build_actions
from utils.sheets_writer import write_df

st.set_page_config(page_title="Trade / Action Hub", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("🧭 Trade / Action Hub")
st.caption("One place for **Reorder**, **Compliance**, and **PPC negatives**. Color-coded by urgency and exportable to Google Sheets.")

th = load_thresholds()
doc_low = int(th.get("doc_days_low", 10))
comp_days = int(th.get("compliance_due_days", 30))
ppc_spend = float(th.get("ppc_min_spend", 10.0))
ppc_clicks = int(th.get("ppc_min_clicks", 12))

st.sidebar.subheader("Thresholds")
doc_low = st.sidebar.number_input("Low DoC threshold", 1, 120, doc_low)
comp_days = st.sidebar.number_input("Compliance due window (days)", 1, 180, comp_days)
ppc_spend = st.sidebar.number_input("PPC surge min spend ($)", 0.0, 1000.0, ppc_spend, 0.5)
ppc_clicks = st.sidebar.number_input("PPC surge min clicks", 0, 1000, ppc_clicks)

# Build fresh
th_live = {"doc_days_low": doc_low, "compliance_due_days": comp_days, "ppc_min_spend": ppc_spend, "ppc_min_clicks": ppc_clicks}
actions = build_actions(th_live)

# KPI tiles
red = int((actions["severity"]=="red").sum()) if not actions.empty else 0
yel = int((actions["severity"]=="yellow").sum()) if not actions.empty else 0
tot = len(actions)
c1,c2,c3 = st.columns(3)
c1.metric("Critical", red)
c2.metric("Attention", yel)
c3.metric("Total", tot)

st.subheader("Action Items")
if actions.empty:
    st.info("No actions right now. All clear ✅")
else:
    # Light styling
    def style_rows(df: pd.DataFrame):
        styles = []
        for _, r in df.iterrows():
            if r["severity"]=="red":
                styles.append(["background-color: rgba(255,0,0,0.18)"]*len(df.columns))
            elif r["severity"]=="yellow":
                styles.append(["background-color: rgba(255,165,0,0.18)"]*len(df.columns))
            else:
                styles.append([""]*len(df.columns))
        return pd.DataFrame(styles, index=df.index, columns=df.columns)
    st.dataframe(actions.style.apply(style_rows, axis=None), use_container_width=True, hide_index=True)

    cA, cB = st.columns(2)
    if cA.button("📤 Export to Google Sheet → actions_out"):
        st.success(write_df("actions_out", actions))
    cB.download_button("⬇️ Download CSV", data=actions.to_csv(index=False).encode("utf-8"),
                       file_name="actions_out.csv", mime="text/csv")

st.caption("Tip: thresholds are read from the optional `alerts_settings` tab at snapshot time; here you can adjust them ad‑hoc without changing the sheet.")
