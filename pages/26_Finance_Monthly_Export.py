# pages/26_Finance_Monthly_Export.py
import streamlit as st
from datetime import date
from utils.exporters import export_finance_monthly

st.set_page_config(page_title="Finance Monthly Export", layout="wide")
st.title("Finance Monthly Export")

today = date.today()
col1, col2 = st.columns(2)
year = col1.number_input("Year", min_value=2018, max_value=2100, value=today.year, step=1)
month = col2.number_input("Month", min_value=1, max_value=12, value=today.month, step=1)

if st.button("Generate CSV"):
    with st.spinner("Building monthly export..."):
        try:
            csv_bytes = export_finance_monthly(int(year), int(month))
            st.success("Export ready.")
            st.download_button("⬇️ Download CSV", data=csv_bytes,
                               file_name=f"finance_{int(year)}_{int(month):02d}.csv",
                               mime="text/csv")
        except Exception as e:
            st.error(f"Export failed: {e}")
            st.info("Make sure Ads metrics exist for the selected month (run Metrics tab or nightly cache).")
else:
    st.caption("Pick a year/month and click Generate CSV.")
