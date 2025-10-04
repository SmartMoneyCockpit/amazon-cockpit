
import streamlit as st
import pandas as pd
from utils.promote_restore import list_staging_dirs, scan_diff, promote_to_live
from utils.logs import log_job

st.set_page_config(page_title="Restore Manager", layout="wide")
st.title("Restore Manager")

st.caption("Promote a verified staging restore back to live. Menu order is unchanged.")

# List staging directories
dirs = list_staging_dirs()
if not dirs:
    st.info("No staging restores found. Use Backup Manager → Restore to Staging first.")
    st.stop()

sel = st.selectbox("Select a staging restore folder", options=dirs, index=0)

st.subheader("Preview Differences")
roots = st.multiselect("Restrict to folders (optional)", ["pages","modules","components","utils","tools","infra",".streamlit"], default=[])
preview = scan_diff(sel, roots=roots or None)
c1, c2, c3, c4 = st.columns(4)
c1.metric("New files", preview.get("new",0))
c2.metric("Updated files", preview.get("updated",0))
c3.metric("Unchanged", preview.get("same",0))
c4.metric("Total (staging)", preview.get("total_staging_files",0))

st.divider()
st.subheader("Promote to Live")

agree = st.checkbox("I understand this will copy files from staging into my live repo and back up any overwritten files.")
if st.button("Promote Now", disabled=not agree):
    try:
        backup_path, counts = promote_to_live(sel, roots=roots or None)
        log_job("promote_restore", "ok", f"Promoted {sel} to live", {"counts": counts, "backup": backup_path})
        st.success(f"Promoted successfully. Pre-promotion backup saved at: {backup_path}")
        st.json(counts)
    except Exception as e:
        try:
            log_job("promote_restore", "error", str(e), {"staging": sel})
        except Exception:
            pass
        st.error(f"Promotion failed: {e}")
