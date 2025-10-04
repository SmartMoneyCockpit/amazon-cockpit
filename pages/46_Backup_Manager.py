import os, io, pathlib
import streamlit as st
from utils.backup import create_backup, list_backups, latest_backup

st.set_page_config(page_title="Backup Manager", layout="wide")
st.title("Backup Manager")

st.caption("Create and download cockpit backups. This page is menu-safe and does not alter your sidebar.")

# Actions
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("Create Backup Now"):
        path = create_backup()
        st.success(f"Backup created: {path}")
with c2:
    latest = latest_backup()
    if latest and st.button("Download Latest"):
        with open(latest, "rb") as f:
            st.download_button("Click to download", data=f.read(), file_name=os.path.basename(latest))
with c3:
    if st.button("Refresh List"):
        st.experimental_rerun()

st.divider()
st.subheader("Existing Backups")
paths = list_backups()
if not paths:
    st.info("No backups yet. Click 'Create Backup Now' to make your first one.")
else:
    for p in paths:
        col1, col2 = st.columns([5,1])
        with col1:
            st.write(p)
        with col2:
            with open(p, "rb") as f:
                st.download_button("Download", data=f.read(), file_name=os.path.basename(p), key=p)
