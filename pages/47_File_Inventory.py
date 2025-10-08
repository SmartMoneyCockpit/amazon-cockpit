
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


# --- [61–65] Open Latest Snapshot ---
import os, glob, streamlit as _st
_st.subheader("Open Latest Snapshot")
try:
    files = sorted(glob.glob(os.path.join("snapshots","snapshot_*.*")), key=lambda p: os.path.getmtime(p), reverse=True)
    latest_csv = next((p for p in files if p.endswith(".csv")), None)
    latest_md  = next((p for p in files if p.endswith(".md")), None)
    latest_txt = next((p for p in files if p.endswith(".txt")), None)
    cols = _st.columns(3)
    if latest_csv:
        with open(latest_csv, "rb") as fh:
            cols[0].download_button("Download latest CSV", data=fh.read(), file_name=os.path.basename(latest_csv), use_container_width=True)
    else:
        cols[0].button("No CSV yet", disabled=True, use_container_width=True)
    if latest_md:
        with open(latest_md, "rb") as fh:
            cols[1].download_button("Download latest MD", data=fh.read(), file_name=os.path.basename(latest_md), use_container_width=True)
    else:
        cols[1].button("No MD yet", disabled=True, use_container_width=True)
    if latest_txt:
        with open(latest_txt, "rb") as fh:
            cols[2].download_button("Download latest TXT", data=fh.read(), file_name=os.path.basename(latest_txt), use_container_width=True)
    else:
        cols[2].button("No TXT yet", disabled=True, use_container_width=True)
except Exception:
    _st.info("No snapshot artifacts found yet.")
