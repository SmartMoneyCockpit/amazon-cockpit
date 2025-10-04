import streamlit as st
import pandas as pd
from infra.sheets_client import SheetsClient

st.set_page_config(page_title="Cockpit Settings", layout="wide")
st.title("Settings")

c1, c2 = st.columns(2)
with c1:
    tz = st.text_input("Timezone", "America/Los_Angeles")
    cur = st.text_input("Base currency", "USD", max_chars=3)
    rsd = st.text_input("Report start date (YYYY-MM-DD)", "2025-01-01")
with c2:
    ads = st.toggle("Ads enabled", True)
    snap = st.toggle("Auto Snapshot PDF", True)

st.divider()
if st.button("Save Settings"):
    try:
        sc = SheetsClient()
        rows = [
            {"key": "timezone", "value": tz},
            {"key": "base_currency", "value": cur.upper()},
            {"key": "report_start_date", "value": rsd},
            {"key": "ads_enabled", "value": ads},
            {"key": "auto_snapshot_pdf", "value": snap},
        ]
        sc.write_table("Settings", rows, clear=True)
        st.success("Saved to Google Sheets.")
    except Exception as e:
        st.warning(f"Could not save: {e}")
