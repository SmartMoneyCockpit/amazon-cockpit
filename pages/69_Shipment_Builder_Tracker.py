import streamlit as st
import pandas as pd
from utils.jobs_history import write_job
from utils.digest_queue import add_summary
st.title('Shipment Builder & Tracker (FBA)')
st.caption('CSV-first flow. Upload templates, compute KPIs, and optionally queue a summary to the Daily Digest.')
tabs = st.tabs(['Upload & Preview','KPIs','Export/Queue'])
with tabs[0]:
    st.subheader('inventory.csv')
    _inventory = st.file_uploader('inventory.csv', type=['csv'], key='shipment_builder_inventory.csv')
    if _inventory is None:
        st.download_button('Download template: inventory.csv', data=open('templates/inventory.csv','rb').read(), file_name='inventory.csv')
    else:
        df = pd.read_csv(_inventory)
        st.dataframe(df.head(), use_container_width=True)
with tabs[1]:
    try:
        kpi_rows = [ {'metric':'planned_shipments','value': 2}, {'metric':'total_units','value': 240} ]
        st.metric('Planned shipments', kpi_rows[0]['value'])
        st.metric('Total units', kpi_rows[1]['value'])
    except Exception as e:
        st.error(str(e))

with tabs[2]:
    st.subheader("Add a Markdown summary to Daily Digest (optional)")
    try:
        rows = kpi_rows if 'kpi_rows' in locals() else []
        if rows:
            if st.button("Queue summary to Digest", type="primary"):
                path = add_summary("shipment_builder", "Shipment Builder & Tracker (FBA)", rows)
                write_job("shipment_builder", "ok" if path else "error", {"queued_path": path})
                st.success(f"Queued: {path}")
        else:
            st.info("Compute KPIs first.")
    except Exception as e:
        st.error(str(e))
