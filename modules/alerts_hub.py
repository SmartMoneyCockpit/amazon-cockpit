import streamlit as st
import pandas as pd
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.alerts import alerts_to_df

def alerts_hub_view():
    section_header("🚨 Alerts Hub")
    st.caption("Only‑when‑true: low stock, suppressed listings, ACoS breach. This hub aggregates alerts from other tabs.")
    raw = st.session_state.get("alerts_buffer", [])
    df = alerts_to_df([type("A",(object,),r) for r in raw]) if raw else pd.DataFrame(columns=["severity","message","source"])

    if df.empty:
        st.success("No active alerts.")
        return

    st.dataframe(df, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.download_button("CSV", df_to_csv_bytes(df), file_name="alerts.csv")
    c2.download_button("XLSX", df_to_xlsx_bytes(df), file_name="alerts.xlsx")
    c3.download_button("PDF", simple_pdf_bytes("Alerts", df), file_name="alerts.pdf")
