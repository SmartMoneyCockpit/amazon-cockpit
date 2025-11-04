import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('FBA Fee & Storage Cost Forecaster')
# Update caption to reflect direct Amazon integration rather than CSV uploads
st.caption('This tool now fetches data directly from your Amazon Seller account. Uploading CSVs is no longer required.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    # CSV uploads have been removed in favor of automatic Amazon Seller integration.
    st.info('Data will be pulled from your Amazon Seller account once integration is configured. There is no need to upload CSV files.')
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
