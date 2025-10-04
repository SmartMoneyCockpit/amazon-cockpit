import datetime as dt
import pandas as pd
import streamlit as st
from infra.sheets_client import SheetsClient
from utils.exporters import export_finance_monthly

st.set_page_config(page_title="Finance Monthly Export", layout="wide")
st.title("Finance Monthly Export")

st.caption("Exports the 'Finances' worksheet for a chosen month to snapshots/YYYY-MM/. PDF is optional (auto if reportlab is installed).")

# Pick month/year
today = dt.date.today()
col1, col2 = st.columns([1,2])
with col1:
    year = st.number_input("Year", min_value=2000, max_value=today.year+1, value=today.year, step=1)
with col2:
    month = st.selectbox("Month", list(range(1,13)), index=today.month-1, format_func=lambda m: f"{m:02d}")

def _read_finances():
    try:
        sc = SheetsClient()
        rows = sc.read_table("Finances")
        return pd.DataFrame(rows)
    except Exception as e:
        st.info("Google Sheets not connected — exporting an empty CSV.")
        return pd.DataFrame(columns=["date","gmv","acos","tacos","refund_rate"])

if st.button("Export Now"):
    df = _read_finances()
    csv_path, maybe_pdf = export_finance_monthly(df, int(year), int(month))
    st.success(f"Exported CSV to: {csv_path}")
    if maybe_pdf is not None:
        st.success(f"Exported PDF to: {maybe_pdf}")
    else:
        st.info("PDF skipped (install 'reportlab' to enable PDF output).")
