
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

# Optional UI helpers
try:
    from utils.ui_refinements import inject_css, sev_badge, sheet_link
except Exception:
    def inject_css(): pass
    def sev_badge(x): return x
    def sheet_link(tab): return f"<span>Sheet: {tab}</span>"

# Builder (with margins integration if available)
try:
    from utils.actions_plus import build_actions_with_margins, load_thresholds
except Exception:
    from utils.actions import build_actions as build_actions_with_margins
    from utils.alerts import load_thresholds

st.set_page_config(page_title="Trade / Action Hub", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

inject_css()
st.title("🧭 Trade / Action Hub")
th = load_thresholds() if callable(load_thresholds) else {}

actions = build_actions_with_margins(th) if callable(build_actions_with_margins) else pd.DataFrame()

red = int((actions["severity"].astype(str)=="red").sum()) if "severity" in actions.columns and not actions.empty else 0
yel = int((actions["severity"].astype(str)=="yellow").sum()) if "severity" in actions.columns and not actions.empty else 0
tot = len(actions)

c1,c2,c3 = st.columns(3)
c1.metric("Critical", red)
c2.metric("Attention", yel)
c3.metric("Total", tot)

st.write(sheet_link("actions_out"), unsafe_allow_html=True)
if actions.empty:
    st.info("No actions right now. All clear ✅")
else:
    dfv = actions.copy()
    if "severity" in dfv.columns:
        dfv["severity"] = dfv["severity"].apply(sev_badge)
    st.dataframe(dfv, use_container_width=True, hide_index=True)
