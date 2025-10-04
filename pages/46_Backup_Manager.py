
import os, io, json
import streamlit as st
import pandas as pd
from utils.backup import create_backup, list_backups, latest_backup
from utils.restore import list_zip_contents, restore_to_staging, tree_preview

st.set_page_config(page_title="Backup Manager", layout="wide")
st.title("Backup Manager")

st.caption("Create, download, and (safely) restore backups to a staging folder. This is menu-safe and does not alter your sidebar.")

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
        with st.expander(p, expanded=False):
            # Preview top of ZIP contents
            preview = list_zip_contents(p, max_items=150)
            if preview:
                st.caption("Top files in ZIP:")
                st.code("\n".join(preview[:50]))
            # Buttons per backup
            b1, b2 = st.columns([1,1])
            with b1:
                with open(p, "rb") as f:
                    st.download_button("Download", data=f.read(), file_name=os.path.basename(p), key="dl_"+p)
            with b2:
                if st.button("Restore to Staging", key="rs_"+p):
                    target = restore_to_staging(p)
                    st.success(f"Restored to staging: {target}")
                    # Show a compact tree preview from staging
                    rows = tree_preview(target, max_entries=300)
                    if rows:
                        df = pd.DataFrame(rows)
                        st.dataframe(df, use_container_width=True)
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button("Download staging tree CSV", data=csv, file_name="staging_tree.csv", mime="text/csv")

st.divider()
st.subheader("How to Complete a Restore (Manual, Safe)")
st.markdown("""
1. Use **Restore to Staging** on a chosen backup (above).  
2. Review the extracted files under `restore_staging/...` and confirm.  
3. Make a live backup (Utilities → **Backup Manager** → **Create Backup Now**) before replacing.  
4. Replace live files with the staged copy using your preferred method (git / deploy / Render shell).  
""")
