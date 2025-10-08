
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


# --- [89] Type-aware preview (JSON/CSV/MD) ---
import streamlit as _st
import pandas as _pd
import json as _json

if 'full' in locals() and full and os.path.exists(full):
    ext = os.path.splitext(full)[1].lower()
    _st.subheader("Preview (type-aware)")
    try:
        if ext == ".json":
            txt = open(full,"r",encoding="utf-8").read()[:4000]
            try: obj = _json.loads(txt)
            except Exception: obj = None
            if obj: _st.json(obj)
            else: _st.code(txt)
        elif ext == ".csv":
            try:
                df = _pd.read_csv(full).head(50)
                _st.dataframe(df, use_container_width=True)
            except Exception as e:
                _st.error(f"CSV preview error: {e}")
        elif ext == ".md":
            txt = open(full,"r",encoding="utf-8").read()[:4000]
            _st.markdown(txt)
        else:
            _st.caption("Unknown type; showing raw head:")
            _st.code(open(full,'r',encoding='utf-8',errors='ignore').read()[:1000])
    except Exception as e:
        _st.error(str(e))
