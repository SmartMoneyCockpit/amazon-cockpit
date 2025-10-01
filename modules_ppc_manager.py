import streamlit as st
import pandas as pd
from utils.data import load_sample_df
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.alerts import ppc_alerts

def ppc_manager_view():
    section_header("📈 PPC Manager")
    st.caption("Budgets, ACoS, ROAS, and campaign drill‑downs.")
    df = load_sample_df("ppc")
    st.line_chart(df.set_index("Date")[["Impressions","Clicks","Orders"]])
    st.area_chart(df.set_index("Date")[["Spend"]])
    st.bar_chart(df.set_index("Date")[["ROAS"]])
    st.dataframe(df, use_container_width=True)

    cols = st.columns(3)
    cols[0].metric("Avg ACoS", f"{df['ACoS%'].mean():.1f}%")
    cols[1].metric("Avg ROAS", f"{df['ROAS'].mean():.2f}")
    cols[2].metric("Spend (14d)", f"${df['Spend'].sum():,.0f}")

    with st.expander("⬇️ Export"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(df), file_name="ppc_manager.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(df), file_name="ppc_manager.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("PPC Manager", df), file_name="ppc_manager.pdf")

    # Alerts from PPC data
    alerts = ppc_alerts(df, acos_threshold=35.0)
    if alerts:
        st.warning(f"{len(alerts)} PPC alert(s) detected — see Alerts Hub tab.")
        st.session_state.setdefault("alerts_buffer", [])
        st.session_state["alerts_buffer"].extend([a.__dict__ for a in alerts])
