import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('FBA Fee & Storage Cost Forecaster')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('fee_table.csv')
    _fee_table = st.file_uploader('fee_table.csv', type=['csv'], key='fba_fee_forecast_fee_table.csv')
    if _fee_table is None:
        st.download_button('Download template: fee_table.csv', data=open('templates/fee_table.csv','rb').read(), file_name='fee_table.csv')
    else:
        df = pd.read_csv(_fee_table)
        st.dataframe(df.head(), use_container_width=True)
    st.subheader('storage_rates.csv')
    _storage_rates = st.file_uploader('storage_rates.csv', type=['csv'], key='fba_fee_forecast_storage_rates.csv')
    if _storage_rates is None:
        st.download_button('Download template: storage_rates.csv', data=open('templates/storage_rates.csv','rb').read(), file_name='storage_rates.csv')
    else:
        df = pd.read_csv(_storage_rates)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'avg_fba_fee','value': 3.40}, {'metric':'storage_cost_share','value': 0.06} ]
        st.metric('Avg FBA fee', f"${{kpi_rows[0]['value']:.2f}}")
        st.metric('Storage cost / GMV', f"{kpi_rows[1]['value']*100:.0f}%")
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("fba_fee_forecast", "FBA Fee & Storage Cost Forecaster", rows)
                write_job("fba_fee_forecast", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
