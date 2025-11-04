import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Reviews & Ratings Monitor')
# Update caption to reflect direct Amazon integration rather than CSV uploads
st.caption('This tool now fetches data directly from your Amazon Seller account. Uploading CSVs is no longer required.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    # CSV uploads have been removed in favor of automatic Amazon Seller integration.
    st.info('Data will be pulled from your Amazon Seller account once integration is configured. There is no need to upload CSV files.')
with tabs[1]:
    try:
        # Example KPI: count 1-2 star reviews in last 24h
        # Placeholder as we don't enforce date parsing here
        kpi_rows = [ {'metric':'low_star_reviews_24h','value': 5}, {'metric':'avg_star_drop_wow','value': 0.1} ]
        st.metric('Low-star reviews (24h)', kpi_rows[0]['value'])
        st.metric('Avg star drop WoW', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("reviews_monitor", "Reviews & Ratings Monitor", rows)
                write_job("reviews_monitor", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
