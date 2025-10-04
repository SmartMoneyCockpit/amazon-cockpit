import streamlit as st
import pandas as pd
from infra.sheets_client import SheetsClient

st.set_page_config(page_title="Cockpit Settings", layout="wide")
st.title("Settings")

cols = st.columns(2)
with cols[0]:
    tz = st.text_input("Timezone", value="America/Los_Angeles")
    cur = st.text_input("Base currency", value="USD", max_chars=3)
    rsd = st.text_input("Report start date (YYYY-MM-DD)", value="2025-01-01")

with cols[1]:
    ads = st.toggle("Ads enabled", value=True)
    snap = st.toggle("Auto Snapshot PDF", value=True)

st.divider()
st.subheader("Persist to Google Sheets")

status = st.empty()

def _write_to_sheets(data: dict):
    try:
        sc = SheetsClient()
        rows = [{"key": k, "value": str(v)} for k, v in data.items()]
        sc.write_table("Settings", rows, clear=True)
        return True, "Saved to Google Sheets: 'Settings'"
    except Exception as e:
        return False, f"Sheets write failed: {e}"

if st.button("Save Settings"):
    data = {
        "timezone": tz,
        "base_currency": cur.upper(),
        "report_start_date": rsd,
        "ads_enabled": ads,
        "auto_snapshot_pdf": snap,
    }
    ok, msg = _write_to_sheets(data)
    if ok:
        status.success(msg)
    else:
        status.warning(msg + " (not fatal)")
