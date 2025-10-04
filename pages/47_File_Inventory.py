
import io, datetime as dt
import pandas as pd
import streamlit as st
from utils.file_inventory import iter_files, add_checksums

st.set_page_config(page_title="File Inventory", layout="wide")
st.title("File Inventory & Repo Hygiene")

st.caption("Generate an inventory of files with size, modified time, and optional SHA-1 checksums. Menu order is unchanged.")

# Controls
c1, c2, c3, c4 = st.columns([1,1,1,2])
with c1:
    include_sha1 = st.checkbox("Include SHA-1 (<=5MB)", value=True)
with c2:
    min_size = st.number_input("Min size (KB)", min_value=0, value=0, step=1)
with c3:
    large_only = st.checkbox("Show > 2MB", value=False)
with c4:
    st.caption("Tip: Use this before upgrades to spot large/old files.")

rows = iter_files(["pages","modules","components","utils","tools","infra",".streamlit","."])

df = pd.DataFrame(rows)
if df.empty:
    st.info("No files found.")
else:
    # Filters
    if min_size:
        df = df[df["size"] >= (min_size * 1024)]
    if large_only:
        df = df[df["size"] > 2 * 1024 * 1024]

    # Checksums
    if include_sha1 and not df.empty:
        df = pd.DataFrame(add_checksums(df.to_dict(orient="records")))

    df_sorted = df.sort_values("size", ascending=False)

    st.subheader("Inventory")
    with st.expander("Show table", expanded=True):
        st.dataframe(df_sorted, use_container_width=True)

    # Exports
    st.divider()
    st.subheader("Export")
    csv_bytes = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name=f"file_inventory_{dt.date.today().isoformat()}.csv", mime="text/csv")
