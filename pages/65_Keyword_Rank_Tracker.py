import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Keyword Rank Tracker & Competitor Gap')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('keywords.csv')
    _keywords = st.file_uploader('keywords.csv', type=['csv'], key='keyword_rank_keywords.csv')
    if _keywords is None:
        st.download_button('Download template: keywords.csv', data=open('templates/keywords.csv','rb').read(), file_name='keywords.csv')
    else:
        df = pd.read_csv(_keywords)
        st.dataframe(df.head(), use_container_width=True)
    st.subheader('competitors.csv')
    _competitors = st.file_uploader('competitors.csv', type=['csv'], key='keyword_rank_competitors.csv')
    if _competitors is None:
        st.download_button('Download template: competitors.csv', data=open('templates/competitors.csv','rb').read(), file_name='competitors.csv')
    else:
        df = pd.read_csv(_competitors)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'keywords_tracked','value': 120}, {'metric':'avg_rank','value': 17} ]
        st.metric('Keywords tracked', kpi_rows[0]['value'])
        st.metric('Avg rank', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("keyword_rank", "Keyword Rank Tracker & Competitor Gap", rows)
                write_job("keyword_rank", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
