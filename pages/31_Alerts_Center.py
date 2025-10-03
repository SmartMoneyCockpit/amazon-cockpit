
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec

# Optional UI helpers (Day-22). If unavailable, pages still work.
try:
    from utils.ui_refinements import inject_css, sev_badge, sheet_link
except Exception:
    def inject_css(): pass
    def sev_badge(x): return x
    def sheet_link(tab): return f"<span>Sheet: {tab}</span>"

# Original alerts API
try:
    from utils.alerts_plus import load_thresholds, low_doc_alerts, compliance_due_alerts, ppc_negatives_surge, margin_breach_alerts
except Exception:
    from utils.alerts import load_thresholds, low_doc_alerts, compliance_due_alerts, ppc_negatives_surge
    def margin_breach_alerts(net_min, gross_min):
        return pd.DataFrame()

from utils.sheets_writer import write_df

st.set_page_config(page_title="Alerts Center", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

inject_css()
st.title("🚨 Alerts Center")
th = load_thresholds()
doc_thresh = int(th.get("doc_days_low", 10))
comp_days = int(th.get("compliance_due_days", 30))
ppc_spend = float(th.get("ppc_min_spend", 10.0))
ppc_clicks = int(th.get("ppc_min_clicks", 12))
net_min = float(th.get("net_margin_min_pct", 0.0)) if "net_margin_min_pct" in th else 0.0
gross_min = float(th.get("gross_margin_min_pct", 15.0)) if "gross_margin_min_pct" in th else 15.0

c1, c2, c3 = st.columns(3)
doc_thresh = c1.number_input("Low DoC threshold", 1, 120, doc_thresh)
comp_days = c2.number_input("Compliance due (days)", 1, 180, comp_days)
ppc_spend = c3.number_input("PPC surge min spend ($)", 0.0, 1000.0, ppc_spend, 0.5)
ppc_clicks = st.number_input("PPC surge min clicks (no orders)", 0, 1000, ppc_clicks, 1)

# Low DoC
st.subheader("📦 Low Days of Cover")
doc_df = low_doc_alerts(doc_thresh)
st.write(sheet_link("alerts_out_low_doc"), unsafe_allow_html=True)
st.dataframe(doc_df if not doc_df.empty else pd.DataFrame(), use_container_width=True, hide_index=True)
if not doc_df.empty and st.button("📤 Export low DoC → alerts_out_low_doc"):
    st.success(write_df("alerts_out_low_doc", doc_df))

# Compliance
st.subheader("🧾 Compliance Expiring")
comp_df = compliance_due_alerts(comp_days)
st.write(sheet_link("alerts_out_compliance"), unsafe_allow_html=True)
st.dataframe(comp_df if not comp_df.empty else pd.DataFrame(), use_container_width=True, hide_index=True)
if not comp_df.empty and st.button("📤 Export compliance → alerts_out_compliance"):
    st.success(write_df("alerts_out_compliance", comp_df))

# PPC
st.subheader("🔎 PPC Negatives / Surge Candidates")
ppc_df = ppc_negatives_surge(ppc_spend, ppc_clicks)
st.write(sheet_link("alerts_out_ppc"), unsafe_allow_html=True)
st.dataframe(ppc_df if not ppc_df.empty else pd.DataFrame(), use_container_width=True, hide_index=True)
if not ppc_df.empty and st.button("📤 Export PPC alerts → alerts_out_ppc"):
    st.success(write_df("alerts_out_ppc", ppc_df))

# Margins
st.subheader("📉 Margin Breaches")
mb_df = margin_breach_alerts(net_min, gross_min)
st.write(sheet_link("alerts_out_margins"), unsafe_allow_html=True)
st.dataframe(mb_df if not mb_df.empty else pd.DataFrame(), use_container_width=True, hide_index=True)
if not mb_df.empty and st.button("📤 Export margins → alerts_out_margins"):
    st.success(write_df("alerts_out_margins", mb_df))
