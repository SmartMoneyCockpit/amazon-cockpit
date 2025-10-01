import streamlit as st
from utils.layout import section_header

def alerts_hub_view():
    section_header("🚨 Alerts Hub")
    st.caption("Only‑when‑true: low stock, suppressed listings, ACoS breach.")
    st.write("No active alerts (sample).")
    st.info("Next: add rules engine + email webhook; store alert history in Sheets/DB.")
