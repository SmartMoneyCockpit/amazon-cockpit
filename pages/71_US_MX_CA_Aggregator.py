import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('US–MX–CA Aggregator (FX-aware)')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('summary.csv')
    _summary = st.file_uploader('summary.csv', type=['csv'], key='us_mx_ca_agg_summary.csv')
    if _summary is None:
        st.download_button('Download template: summary.csv', data=open('templates/summary.csv','rb').read(), file_name='summary.csv')
    else:
        df = pd.read_csv(_summary)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'usdmxn_fx','value': 19.5}, {'metric':'gmv_usd','value': 2400} ]
        st.metric('USDMXN (ref)', kpi_rows[0]['value'])
        st.metric('GMV (USD)', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("us_mx_ca_agg", "US–MX–CA Aggregator (FX-aware)", rows)
                write_job("us_mx_ca_agg", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
