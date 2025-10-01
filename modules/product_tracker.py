import streamlit as st
import pandas as pd
from utils.data import load_sheet, load_sample_df
from utils.layout import section_header
from utils.export import df_to_csv_bytes, df_to_xlsx_bytes, simple_pdf_bytes
from utils.alerts import product_alerts

def product_tracker_view():
    section_header("📦 Product Tracker")
    st.caption("Sessions, CVR, units, inventory, reviews. Replace sample data with SP‑API/Sheets later.")

    # Try loading from Sheets if configured (uses same function; sheet id resolved at secrets level in your app)
    df = load_sample_df("product")
    st.dataframe(df, use_container_width=True)

    kpis = st.columns(4)
    kpis[0].metric("Total Units (14d)", int(df["Units"].sum()))
    kpis[1].metric("Avg CVR", f"{df['CVR%'].mean():.1f}%")
    kpis[2].metric("Avg Stars", f"{df['Stars'].mean():.2f}")
    kpis[3].metric("At Risk (<10 DoC)", int((df['Days of Cover']<10).sum()))

    # Exports
    with st.expander("⬇️ Export"):
        c1, c2, c3 = st.columns(3)
        c1.download_button("CSV", df_to_csv_bytes(df), file_name="product_tracker.csv")
        c2.download_button("XLSX", df_to_xlsx_bytes(df), file_name="product_tracker.xlsx")
        c3.download_button("PDF", simple_pdf_bytes("Product Tracker", df), file_name="product_tracker.pdf")

    # Alerts from product data
    p_alerts = product_alerts(df)
    if p_alerts:
        st.warning(f"{len(p_alerts)} product alert(s) detected — see Alerts Hub tab.")
        # stash in session for Alerts Hub
        st.session_state.setdefault("alerts_buffer", [])
        st.session_state["alerts_buffer"].extend([a.__dict__ for a in p_alerts])
