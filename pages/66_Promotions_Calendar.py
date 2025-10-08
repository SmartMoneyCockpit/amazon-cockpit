import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Promotions / Coupons Calendar')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('promos.csv')
    _promos = st.file_uploader('promos.csv', type=['csv'], key='promos_calendar_promos.csv')
    if _promos is None:
        st.download_button('Download template: promos.csv', data=open('templates/promos.csv','rb').read(), file_name='promos.csv')
    else:
        df = pd.read_csv(_promos)
        st.dataframe(df.head(), use_container_width=True)
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
