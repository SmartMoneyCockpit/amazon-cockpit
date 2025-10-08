import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Reviews & Ratings Monitor')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('reviews.csv')
    _reviews = st.file_uploader('reviews.csv', type=['csv'], key='reviews_monitor_reviews.csv')
    if _reviews is None:
        st.download_button('Download template: reviews.csv', data=open('templates/reviews.csv','rb').read(), file_name='reviews.csv')
    else:
        df = pd.read_csv(_reviews)
        st.dataframe(df.head(), use_container_width=True)
    st.subheader('ratings.csv')
    _ratings = st.file_uploader('ratings.csv', type=['csv'], key='reviews_monitor_ratings.csv')
    if _ratings is None:
        st.download_button('Download template: ratings.csv', data=open('templates/ratings.csv','rb').read(), file_name='ratings.csv')
    else:
        df = pd.read_csv(_ratings)
        st.dataframe(df.head(), use_container_width=True)
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
