import streamlit as st
import pandas as pd
from dataclasses import asdict
from infra.sheets_client import SheetsClient
from dataframes.finance import build_kpis
from modules.alerts.rules import Rule, load_rules, save_rules, add_rule, remove_rule
from utils.digest import enqueue

st.set_page_config(page_title="Alerts Center", layout="wide")
st.title("Alerts Center")

st.caption("Create simple rules on Finance metrics. If Google Sheets isn't connected, demo data is used so the UI always works.")

# Load finance rows quietly
def _read_finances():
    try:
        sc = SheetsClient()
        return sc.read_table("Finances")
    except Exception:
        return []

# Build demo/live dataframe
_, finance_df = build_kpis(_read_finances())

with st.expander("Add Rule", expanded=False):
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        metric = st.selectbox("Metric", ["gmv", "acos", "tacos", "refund_rate"], index=0)
    with c2:
        operator = st.selectbox("Operator", [">", "<", ">=", "<=", "crosses_above", "crosses_below"], index=0)
    with c3:
        threshold = st.number_input("Threshold", value=0.20 if metric in ("acos","tacos","refund_rate") else 1000.0, step=0.01, format="%.4f")
    lookback = st.number_input("Lookback days (samples)", min_value=2, value=7, step=1)
    name = st.text_input("Optional name/label", value="")
    if st.button("Add Rule", use_container_width=False):
        r = Rule(metric=metric, operator=operator, threshold=float(threshold), lookback_days=int(lookback), name=name or "")
        add_rule(r)
        st.success("Rule added.")

st.subheader("Your Rules")
rules = load_rules()
if not rules:
    st.info("No rules yet. Add one above.")
else:
    for idx, r in enumerate(rules):
        cols = st.columns([3,5,2,2,2])
        with cols[0]: st.write(r.name or f"Rule {idx+1}")
        with cols[1]: st.write(f"{r.metric} {r.operator} {r.threshold}")
        with cols[2]: st.write(f"Lookback: {r.lookback_days}")
        with cols[3]: 
            if st.button("Test", key=f"test_{idx}"):
                passed, reason = r.evaluate(finance_df)
                if passed:
                    st.success(f"PASSED — {reason}")
                else:
                    st.warning(f"Not passed — {reason}")
        with cols[4]:
            if st.button("Delete", key=f"del_{idx}"):
                remove_rule(idx)
                st.experimental_rerun()

st.divider()
st.subheader("Evaluate All & Queue Digest")
if st.button("Evaluate Now"):
    any_hits = False
    for r in load_rules():
        passed, reason = r.evaluate(finance_df)
        if passed:
            any_hits = True
            qpath = enqueue({"type": "alert_hit", "rule": asdict(r), "reason": reason})
    if any_hits:
        st.success(f"Alert(s) queued to: {qpath}")
    else:
        st.info("No alerts triggered.")
