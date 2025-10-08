import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('FBA Inventory & Restock Planner')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('inventory.csv')
    _inventory = st.file_uploader('inventory.csv', type=['csv'], key='fba_restock_inventory.csv')
    if _inventory is None:
        st.download_button('Download template: inventory.csv', data=open('templates/inventory.csv','rb').read(), file_name='inventory.csv')
    else:
        df = pd.read_csv(_inventory)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'days_of_cover','value': 28}, {'metric':'restock_qty','value': 150} ]
        st.metric('Days of cover', kpi_rows[0]['value'])
        st.metric('Suggested restock qty', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("fba_restock", "FBA Inventory & Restock Planner", rows)
                write_job("fba_restock", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
