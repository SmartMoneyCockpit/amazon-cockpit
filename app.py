import os
import streamlit as st
from datetime import datetime
from infra.sheets_client import SheetsClient

st.set_page_config(page_title="Vega Cockpit - Sheets Test", layout="wide")

st.title("Vega Cockpit • Google Sheets Integration")

st.sidebar.header("Utilities")
if st.sidebar.button("Test Google Sheets Connection"):
    try:
        sc = SheetsClient()
        ws = sc.sh.worksheet("Settings")
        ws.append_row([f"ui_ping_at_{datetime.utcnow().isoformat()}", "from streamlit button"])
        st.success("Ping row appended to 'Settings' ✅")
        st.code("Appended: ['ui_ping_at_<utc-iso>', 'from streamlit button']")
    except Exception as e:
        st.error(f"Connection test failed: {e}")

st.subheader("Settings preview")
try:
    sc = SheetsClient()
    rows = sc.read_table("Settings")
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("No rows yet in 'Settings'.")
except Exception as e:
    st.warning(f"Could not load Settings: {e}")