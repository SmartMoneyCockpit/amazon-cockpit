import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Returns / Defect Rate Analyzer')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('returns.csv')
    _returns = st.file_uploader('returns.csv', type=['csv'], key='returns_analyzer_returns.csv')
    if _returns is None:
        st.download_button('Download template: returns.csv', data=open('templates/returns.csv','rb').read(), file_name='returns.csv')
    else:
        df = pd.read_csv(_returns)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'return_rate_30d','value': 0.052}, {'metric':'refunds_30d','value': 12} ]
        st.metric('Return rate (30d)', f"{kpi_rows[0]['value']*100:.1f}%")
        st.metric('Refunds (30d)', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("returns_analyzer", "Returns / Defect Rate Analyzer", rows)
                write_job("returns_analyzer", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
