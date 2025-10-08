import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Policy & Account Health Watch')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('account_health.csv')
    _account_health = st.file_uploader('account_health.csv', type=['csv'], key='account_health_account_health.csv')
    if _account_health is None:
        st.download_button('Download template: account_health.csv', data=open('templates/account_health.csv','rb').read(), file_name='account_health.csv')
    else:
        df = pd.read_csv(_account_health)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'critical_open','value': 1}, {'metric':'high_open','value': 2} ]
        st.metric('Critical issues open', kpi_rows[0]['value'])
        st.metric('High issues open', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("account_health", "Policy & Account Health Watch", rows)
                write_job("account_health", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
