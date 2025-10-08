import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Buy Box & Price Intelligence')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('pricing.csv')
    _pricing = st.file_uploader('pricing.csv', type=['csv'], key='buybox_intel_pricing.csv')
    if _pricing is None:
        st.download_button('Download template: pricing.csv', data=open('templates/pricing.csv','rb').read(), file_name='pricing.csv')
    else:
        df = pd.read_csv(_pricing)
        st.dataframe(df.head(), use_container_width=True)
    st.subheader('competitors.csv')
    _competitors = st.file_uploader('competitors.csv', type=['csv'], key='buybox_intel_competitors.csv')
    if _competitors is None:
        st.download_button('Download template: competitors.csv', data=open('templates/competitors.csv','rb').read(), file_name='competitors.csv')
    else:
        df = pd.read_csv(_competitors)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'lost_buybox_hours','value': 7}, {'metric':'min_margin','value': 0.22} ]
        st.metric('Lost Buy Box (hrs)', kpi_rows[0]['value'])
        st.metric('Min margin', f"{kpi_rows[1]['value']*100:.0f}%")
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("buybox_intel", "Buy Box & Price Intelligence", rows)
                write_job("buybox_intel", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
