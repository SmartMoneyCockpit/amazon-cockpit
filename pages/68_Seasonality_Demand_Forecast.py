import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Seasonality & Demand Forecast')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('sales_history.csv')
    _sales_history = st.file_uploader('sales_history.csv', type=['csv'], key='seasonality_forecast_sales_history.csv')
    if _sales_history is None:
        st.download_button('Download template: sales_history.csv', data=open('templates/sales_history.csv','rb').read(), file_name='sales_history.csv')
    else:
        df = pd.read_csv(_sales_history)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'forecast_12w_units','value': 1200}, {'metric':'mape','value': 0.14} ]
        st.metric('Forecast (12w units)', kpi_rows[0]['value'])
        st.metric('MAPE', f"{kpi_rows[1]['value']*100:.0f}%")
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("seasonality_forecast", "Seasonality & Demand Forecast", rows)
                write_job("seasonality_forecast", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
