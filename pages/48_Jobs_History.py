# pages/48_Jobs_History.py
import streamlit as st
from utils.jobs_history import read_jobs, filter_jobs, read_jobs_raw, extract_error_snippet

st.set_page_config(page_title="Jobs History", layout="wide")
st.title("Jobs History")

# Filters
col1, col2 = st.columns([2,1])
query = col1.text_input("Search (message/job contains)", "")
levels = col2.multiselect("Levels", ["INFO","WARN","ERROR"], default=[])

# Load/Filter
rows = read_jobs(limit=500)
rows = filter_jobs(rows, levels=levels, contains=query)

if not rows:
    st.info("No job entries found yet.")
else:
    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=420)

st.markdown("---")
with st.expander("Raw entries (debug)"):
    st.json(read_jobs_raw()[:50])

st.caption("Tip: nightly jobs write logs to `/data/logs` or `/tmp/vega_data/logs`. "
           "If you want more detail, pipe your cron output to files in that folder.")
