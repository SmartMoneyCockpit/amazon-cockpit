
import streamlit as st
import pandas as pd
from utils.auth import gate
import utils.security as sec
from utils.alerts import load_thresholds, low_doc_alerts, compliance_due_alerts, ppc_negatives_surge
from utils.sheets_writer import write_df

st.set_page_config(page_title="Alerts Center", layout="wide")
sec.enforce()
if not gate(required_admin=False):
    st.stop()

st.title("🚨 Alerts Center")

th = load_thresholds()
c1, c2, c3 = st.columns(3)
doc_thresh = c1.number_input("Low Days of Cover threshold", 1, 120, int(th.get("doc_days_low", 10)))
comp_days = c2.number_input("Compliance due window (days)", 1, 180, int(th.get("compliance_due_days", 30)))
ppc_spend = c3.number_input("PPC surge min spend ($)", 0.0, 1000.0, float(th.get("ppc_min_spend", 10.0)), 0.5)
ppc_clicks = st.number_input("PPC surge min clicks (no orders)", 0, 1000, int(th.get("ppc_min_clicks", 12)), 1)

st.subheader("📦 Low Days of Cover")
doc_df = low_doc_alerts(doc_thresh)
if doc_df.empty:
    st.info("No low-DoC items.")
else:
    st.dataframe(doc_df, use_container_width=True, hide_index=True)
    if st.button("📤 Export low DoC → Sheet (alerts_out_low_doc)"):
        st.success(write_df("alerts_out_low_doc", doc_df))

st.subheader("🧾 Compliance Expiring")
comp_df = compliance_due_alerts(comp_days)
if comp_df.empty:
    st.info("Nothing expiring within window.")
else:
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    if st.button("📤 Export compliance → Sheet (alerts_out_compliance)"):
        st.success(write_df("alerts_out_compliance", comp_df))

st.subheader("🔎 PPC Negatives / Surge Candidates")
ppc_df = ppc_negatives_surge(ppc_spend, ppc_clicks)
if ppc_df.empty:
    st.info("No negatives or surge candidates detected.")
else:
    st.dataframe(ppc_df, use_container_width=True, hide_index=True)
    if st.button("📤 Export PPC alerts → Sheet (alerts_out_ppc)"):
        st.success(write_df("alerts_out_ppc", ppc_df))
