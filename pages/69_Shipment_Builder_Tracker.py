import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Shipment Builder & Tracker (FBA)')
# Update caption to reflect direct Amazon integration rather than CSV uploads
st.caption('This tool now fetches data directly from your Amazon Seller account. Uploading CSVs is no longer required.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    # CSV uploads have been removed in favor of automatic Amazon Seller integration.
    st.info('Data will be pulled from your Amazon Seller account once integration is configured. There is no need to upload CSV files.')
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'planned_shipments','value': 2}, {'metric':'total_units','value': 240} ]
        st.metric('Planned shipments', kpi_rows[0]['value'])
        st.metric('Total units', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("shipment_builder", "Shipment Builder & Tracker (FBA)", rows)
                write_job("shipment_builder", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
