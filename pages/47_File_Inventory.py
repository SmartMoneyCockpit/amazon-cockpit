
import datetime as dt, pandas as pd, streamlit as st
from utils.file_inventory import iter_files, add_checksums
st.set_page_config(page_title="File Inventory", layout="wide"); st.title("File Inventory & Repo Hygiene")
c1,c2,c3,c4=st.columns([1,1,1,2])
with c1: include_sha1=st.checkbox("Include SHA-1 (<=5MB)", True)
with c2: min_size=st.number_input("Min size (KB)", min_value=0, value=0, step=1)
with c3: large_only=st.checkbox("Show > 2MB", False)
with c4: st.caption("Tip: run before upgrades to spot large/old files.")
rows=iter_files(["pages","modules","components","utils","tools","infra",".streamlit","."])
df=pd.DataFrame(rows)
if df.empty: st.info("No files found.")
else:
    if min_size: df=df[df["size"] >= (min_size*1024)]
    if large_only: df=df[df["size"] > 2*1024*1024]
    if include_sha1 and not df.empty: df=pd.DataFrame(add_checksums(df.to_dict(orient="records")))
    df_sorted=df.sort_values("size", ascending=False)
    st.subheader("Inventory"); st.dataframe(df_sorted, use_container_width=True)
    st.divider(); st.subheader("Export")
    st.download_button("Download CSV", data=df_sorted.to_csv(index=False).encode("utf-8"), file_name=f"file_inventory_{dt.date.today().isoformat()}.csv", mime="text/csv")


# [51–55] Size & SHA1 for Snapshots/Backups
import os, time
import streamlit as _st
from utils.hash_utils import file_sha1, file_size_bytes

def _fmt_sz2(n):
    try:
        for unit in ["B","KB","MB","GB"]:
            if n < 1024.0:
                return f"{n:3.1f} {unit}"
            n /= 1024.0
        return f"{n:.1f} TB"
    except Exception:
        return str(n)

def _render_listing(paths):
    for p in paths or []:
        name = os.path.basename(p)
        size = file_size_bytes(p)
        sha1 = file_sha1(p)
        cols = _st.columns([3,1.2,2.8])
        with cols[0]:
            _st.write(f"**{name}**")
            _st.code(p, language="bash")
        with cols[1]:
            _st.write(_fmt_sz2(size))
        with cols[2]:
            _st.code(sha1 or "(sha1 unavailable)")

try:
    if 'snaps' in locals() and snaps:
        _st.caption("Snapshots: size and SHA1")
        _render_listing(snaps)
except Exception: pass
try:
    if 'backs' in locals() and backs:
        _st.caption("Backups: size and SHA1")
        _render_listing(backs)
except Exception: pass
