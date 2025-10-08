import streamlit as st
import pandas as pd
from dataclasses import asdict
from infra.sheets_client import SheetsClient
from dataframes.finance import build_kpis
from modules.alerts.rules import Rule, load_rules, save_rules, add_rule, remove_rule
from utils.digest import enqueue
from utils.alerts_templates import get_templates

st.set_page_config(page_title="Alerts Center", layout="wide")
st.title("Alerts Center")

st.caption("Create rules on Finance metrics. Demo data is used when Google Sheets isn't connected.")

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
        default_thr = 0.20 if metric in ("acos","tacos","refund_rate") else 1000.0
        threshold = st.number_input("Threshold", value=float(default_thr), step=0.01, format="%.4f")
    lookback = st.number_input("Lookback days (samples)", min_value=2, value=7, step=1)
    name = st.text_input("Optional name/label", value="")
    if st.button("Add Rule", use_container_width=False):
        r = Rule(metric=metric, operator=operator, threshold=float(threshold), lookback_days=int(lookback), name=name or "")
        add_rule(r)
        st.success("Rule added.")

with st.expander("Quick Templates", expanded=True):
    templates = get_templates()
    cols = st.columns(5)
    for i, tpl in enumerate(templates):
        col = cols[i % 5]
        with col:
            if st.button(tpl["name"], key=f"tpl_{i}"):
                r = Rule(**tpl)  # Rule fields align with template keys
                add_rule(r)
                st.success(f"Added: {tpl['name']}")

st.subheader("Your Rules")
rules = load_rules()

# Rule filters (local UI only)
fcol1, fcol2 = st.columns([1,1])
with fcol1:
    f_metric = st.multiselect("Filter by metric", ["gmv","acos","tacos","refund_rate"], default=[])
with fcol2:
    f_operator = st.multiselect("Filter by operator", [">","<",">=","<=","crosses_above","crosses_below"], default=[])

filtered_rules = []
for r in rules:
    if f_metric and r.metric not in f_metric:
        continue
    if f_operator and r.operator not in f_operator:
        continue
    filtered_rules.append(r)

if not filtered_rules:
    st.info("No rules to display. Add rules or adjust filters.")
else:
    for idx, r in enumerate(filtered_rules):
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
                # locate index in original list to remove correct item
                orig_idx = rules.index(r)
                remove_rule(orig_idx)
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


# --- [87] Silence alerts for N minutes (writes marker file) ---
import os, json, time, streamlit as _st
SILENCE_PATH = os.path.join("logs","alerts_silenced.json")
_st.subheader("Silence Alerts")
mins = _st.number_input("Minutes to silence", min_value=1, max_value=240, value=30, step=5)
reason = _st.text_input("Reason (optional)", value="manual silence")
if _st.button("Activate Silence", use_container_width=True):
    os.makedirs("logs", exist_ok=True)
    until = int(time.time()) + int(mins)*60
    obj = {"silenced_until": until, "reason": reason}
    try:
        with open(SILENCE_PATH,"w",encoding="utf-8") as f: f.write(json.dumps(obj))
        _st.success(f"Silenced until epoch {until}.")
    except Exception as e:
        _st.error(str(e))
# Show current state
try:
    if os.path.exists(SILENCE_PATH):
        stt = json.loads(open(SILENCE_PATH,"r",encoding="utf-8").read())
        _st.info(f"Silence marker present: {stt}")
    else:
        _st.caption("No active silence marker.")
except Exception as e:
    _st.error(str(e))
