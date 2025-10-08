
import streamlit as st, pandas as pd
from utils.promote_restore import list_staging_dirs, scan_diff, promote_to_live
from utils.logs import log_job
st.set_page_config(page_title="Restore Manager", layout="wide"); st.title("Restore Manager")
dirs=list_staging_dirs()
if not dirs: st.info("No staging restores found. Use Backup Manager → Restore to Staging first."); st.stop()
sel=st.selectbox("Select a staging folder", options=dirs, index=0)
st.subheader("Preview Differences")
roots=st.multiselect("Restrict to folders (optional)", ["pages","modules","components","utils","tools","infra",".streamlit"], default=[])
preview=scan_diff(sel, roots=roots or None)
c1,c2,c3,c4=st.columns(4)
c1.metric("New files", preview.get("new",0)); c2.metric("Updated files", preview.get("updated",0)); c3.metric("Unchanged", preview.get("same",0)); c4.metric("Total (staging)", preview.get("total_staging_files",0))
st.divider(); st.subheader("Promote to Live")
agree=st.checkbox("I understand this copies files from staging into live and backs up overwritten files.")
if st.button("Promote Now", disabled=not agree):
    try:
        backup_path, counts=promote_to_live(sel, roots=roots or None)
        log_job("promote_restore","ok", f"Promoted {sel}", {"counts": counts, "backup": backup_path})
        st.success(f"Promoted. Backup: {backup_path}"); st.json(counts)
    except Exception as e:
        log_job("promote_restore","error", str(e), {"staging": sel}); st.error(f"Failed: {e}")


# --- Available Backups (added) ---
import os, time
import streamlit as st

BACKUPS_DIR = "backups"

def _list_backups():
    try:
        files = [os.path.join(BACKUPS_DIR, f) for f in os.listdir(BACKUPS_DIR)]
        files = [f for f in files if os.path.isfile(f)]
        files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return files
    except Exception:
        return []

st.subheader("Available Backups")
files = _list_backups()
if not files:
    st.info("No backups found.")
else:
    options = [os.path.basename(f) for f in files]
    choice = st.selectbox("Select backup to inspect", options=options, index=0)
    sel = files[options.index(choice)]
    st.code(sel)
    with st.expander("Preview (first 4 KB)", expanded=False):
        try:
            with open(sel, "rb") as fh:
                st.code(fh.read(4096).decode("utf-8", errors="ignore"))
        except Exception as e:
            st.error(str(e))
st.caption("Note: Promotion to Live already performs a pre-backup for safety.")
