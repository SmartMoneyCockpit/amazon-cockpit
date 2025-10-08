
import os, pandas as pd, streamlit as st
from utils.backup import create_backup, list_backups, latest_backup
from utils.restore import list_zip_contents, restore_to_staging, tree_preview
st.set_page_config(page_title="Backup Manager", layout="wide"); st.title("Backup Manager")
st.caption("Create, download, and restore backups to staging (safe).")
c1,c2,c3=st.columns([1,1,1])
with c1:
    if st.button("Create Backup Now"): path=create_backup(); st.success(f"Backup created: {path}")
with c2:
    latest=latest_backup()
    if latest and st.button("Download Latest"):
        with open(latest,"rb") as f: st.download_button("Click to download", data=f.read(), file_name=os.path.basename(latest))
with c3:
    if st.button("Refresh List"): st.experimental_rerun()
st.divider(); st.subheader("Existing Backups")
paths=list_backups()
if not paths: st.info("No backups yet.")
else:
    for p in paths:
        with st.expander(p, expanded=False):
            preview=list_zip_contents(p, 150)
            if preview: st.caption("Top files in ZIP:"); st.code("\n".join(preview[:50]))
            b1,b2=st.columns([1,1])
            with b1:
                with open(p,"rb") as f: st.download_button("Download", data=f.read(), file_name=os.path.basename(p), key="dl_"+p)
            with b2:
                if st.button("Restore to Staging", key="rs_"+p):
                    target=restore_to_staging(p); st.success(f"Restored to staging: {target}")
                    rows=tree_preview(target, 300)
                    if rows:
                        df=pd.DataFrame(rows); st.dataframe(df, use_container_width=True)
                        st.download_button("Download staging tree CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="staging_tree.csv")
st.divider(); st.subheader("How to complete restore")
st.markdown("1) Restore to staging. 2) Validate. 3) Create a live backup. 4) Replace live files.")


# --- Verify SHA-1 (added 59) ---
import streamlit as _st
from utils.hash_utils import file_sha1

if files:
    _st.subheader("Verify SHA-1")
    target = _st.selectbox("Pick a file to verify", options=[os.path.basename(f) for f in files], index=0)
    full = next((f for f in files if os.path.basename(f)==target), None)
    if full and _st.button("Recompute SHA-1", use_container_width=True):
        _st.code(file_sha1(full) or "(not available)")
