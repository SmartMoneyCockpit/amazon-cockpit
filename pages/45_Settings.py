
import streamlit as st
import pandas as pd
from infra.config import load_config
from infra.sheets_client import SheetsClient

st.set_page_config(page_title="Cockpit Settings", layout="wide")
st.title("Settings")

cfg = load_config()

cols = st.columns(2)
with cols[0]:
    tz = st.text_input("Timezone", value=cfg.timezone, help="IANA timezone like America/Los_Angeles")
    cur = st.text_input("Base currency", value=cfg.base_currency, max_chars=3)
    rsd = st.text_input("Report start date (YYYY-MM-DD)", value=cfg.report_start_date)

with cols[1]:
    ads = st.toggle("Ads enabled", value=cfg.ads_enabled)
    snap = st.toggle("Auto Snapshot PDF", value=cfg.auto_snapshot_pdf)

st.divider()
st.subheader("Persist to Google Sheets")

status = st.empty()

def _write_to_sheets(data: dict):
    try:
        sc = SheetsClient()
        # Expect a 'Settings' sheet with key/value columns
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

st.divider()
st.caption("If Google Sheets is unavailable, settings fall back to Streamlit secrets / environment variables.")
