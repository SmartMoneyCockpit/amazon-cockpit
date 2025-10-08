"""
Developer Tools — quick links, smoke tests, and demo seed.
"""
from __future__ import annotations
import os, json, streamlit as st

st.title("Developer Tools")

st.subheader("Quick Links")
# Deep links to commonly used pages that might not be in the menu
st.page_link("pages/31_Alerts_Center.py", label="Alerts Center")
st.page_link("pages/34_Daily_Digest.py", label="Daily Digest")
st.page_link("pages/46_Backup_Manager.py", label="Backup Manager")
st.page_link("pages/47_File_Inventory.py", label="File Inventory")
st.page_link("pages/48_Jobs_History.py", label="Jobs History")
st.page_link("pages/49_Restore_Manager.py", label="Restore Manager", disabled=not os.path.exists("pages/49_Restore_Manager.py"))

st.divider()
st.subheader("Run All Smoke Tests")
try:
    from utils.smoke import run_all as run_smoke
    res = run_smoke()
    c1,c2 = st.columns(2)
    status = "OK" if all(v.get("ok", True) for v in res.values()) else "CHECK"
    c1.metric("Overall", status)
    c2.metric("Checks", len(res))
    st.json(res)
except Exception as e:
    st.error(f"Smoke failed: {e}")

st.divider()
st.subheader("Demo Data Seeder (guarded)")
st.caption("Creates minimal files so you can test UI flows without real data: one snapshot CSV, one digest CSV/MD/TXT into backups/, and a few jobs log lines.")
confirm = st.checkbox("I understand this will create demo artifacts")
if st.button("Create demo data", disabled=not confirm):
    try:
        from workers.demo_seed import main as seed_main
        paths = seed_main()
        st.success("Demo data created:")
        st.json({"created": paths})
    except Exception as e:
        st.error(str(e))
