
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


# --- Snapshots & Backups (added) ---
import os, time
import streamlit as st

def _browse_dir(d: str, limit: int = 50):
    try:
        files = [os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
        files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return files[:limit]
    except Exception:
        return []

st.subheader("Snapshots & Backups")
tab1, tab2 = st.tabs(["snapshots/", "backups/"])
with tab1:
    snaps = _browse_dir("snapshots")
    if not snaps:
        st.info("No snapshots found.")
    else:
        for p in snaps:
            name = os.path.basename(p)
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p)))
            with st.expander(f"{name} — {ts}", expanded=False):
                st.code(p)
                try:
                    with open(p, "rb") as fh:
                        st.download_button("Download", data=fh.read(), file_name=name, use_container_width=True)
                except Exception as e:
                    st.error(str(e))
with tab2:
    backs = _browse_dir("backups")
    if not backs:
        st.info("No backups found.")
    else:
        for p in backs:
            name = os.path.basename(p)
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p)))
            with st.expander(f"{name} — {ts}", expanded=False):
                st.code(p)
                try:
                    with open(p, "rb") as fh:
                        st.download_button("Download", data=fh.read(), file_name=name, use_container_width=True)
                except Exception as e:
                    st.error(str(e))
