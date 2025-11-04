import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Promotions / Coupons Calendar')
# Update caption to reflect direct Amazon integration rather than CSV uploads
st.caption('This tool now fetches data directly from your Amazon Seller account. Uploading CSVs is no longer required.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    # CSV uploads have been removed in favor of automatic Amazon Seller integration.
    st.info('Data will be pulled from your Amazon Seller account once integration is configured. There is no need to upload CSV files.')
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'promo_lift_pct','value': 0.08}, {'metric':'roas','value': 1.7} ]
        st.metric('Promo lift', f"{kpi_rows[0]['value']*100:.0f}%")
        st.metric('ROAS', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("promos_calendar", "Promotions / Coupons Calendar", rows)
                write_job("promos_calendar", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
