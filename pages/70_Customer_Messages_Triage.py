import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Customer Messages Triage')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('messages.csv')
    _messages = st.file_uploader('messages.csv', type=['csv'], key='messages_triage_messages.csv')
    if _messages is None:
        st.download_button('Download template: messages.csv', data=open('templates/messages.csv','rb').read(), file_name='messages.csv')
    else:
        df = pd.read_csv(_messages)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'open_messages','value': 5}, {'metric':'sla_breaches','value': 1} ]
        st.metric('Open messages', kpi_rows[0]['value'])
        st.metric('SLA breaches', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("messages_triage", "Customer Messages Triage", rows)
                write_job("messages_triage", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
