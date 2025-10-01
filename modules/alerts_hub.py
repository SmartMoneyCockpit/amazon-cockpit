
import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.alerts import Alert, alerts_to_df
from utils.export import df_to_xlsx_bytes

def alerts_hub_view():
    section_header("🚨 Alerts Hub")
    st.caption("Only‑when‑true: low stock, suppressed listings, ACoS breach. This hub aggregates alerts from other tabs.")

    # Pull alerts from session or show a sample one
    items = st.session_state.get("alerts", [
        Alert(severity="crit", message="Deindexed: 'nopal capsules' for B0BNOPAL02", source="SEO")
    ])
    df = alerts_to_df(items)
    st.dataframe(df, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="alerts.csv")
    with c2:
        st.download_button("XLSX", data=df_to_xlsx_bytes(df, file_name="alerts.xlsx"), file_name="alerts.xlsx")
    with c3:
        st.download_button("PDF", data=b"", file_name="alerts.pdf", disabled=True, help="PDF export coming soon")
