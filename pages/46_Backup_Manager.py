# pages/46_Backup_Manager.py
import streamlit as st
import os, gzip, shutil
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Backup Manager", layout="wide")
st.title("Backup Manager")

DATA_DIR = os.getenv("VEGA_DATA_DIR", "/data")
BACKUPS = Path(DATA_DIR) / "backups"
DB_PATH = Path(DATA_DIR) / "vega_ads.db"
BACKUPS.mkdir(parents=True, exist_ok=True)

def create_backup():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = BACKUPS / f"vega_ads-{ts}.db.gz"
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    with open(DB_PATH, "rb") as fin, gzip.open(out, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    return out

colA, colB = st.columns([1,1])
with colA:
    if st.button("Create Backup Now"):
        try:
            out = create_backup()
            st.success(f"Backup created: {out.name}")
        except Exception as e:
            st.error(f"Backup failed: {e}")

with colB:
    if st.button("Refresh List"):
        st.experimental_rerun()

# ----- Existing Backups -----
st.subheader("Existing Backups")
files = sorted(BACKUPS.glob("*.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
    st.info("No backups yet.")
else:
    rows = []
    for p in files:
        stat = p.stat()
        rows.append({
            "file": p.name,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "modified_utc": datetime.utcfromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=240)

    # Download first (latest) file convenience
    latest = files[0]
    with open(latest, "rb") as f:
        st.download_button("⬇️ Download latest", data=f.read(),
                           file_name=latest.name, mime="application/gzip")

st.markdown("---")
st.subheader("How to complete restore")
st.markdown("""
1. Restore to staging.  
2. Validate.  
3. Create a live backup.  
4. Replace live files.  
""")
