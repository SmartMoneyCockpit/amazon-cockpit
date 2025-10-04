import os
import streamlit as st
from datetime import datetime
from infra.sheets_client import SheetsClient

# Force the sidebar to be visible on load
st.set_page_config(page_title="Vega Cockpit - Sheets Test",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Hide Streamlit's default page list; we show our own accordion
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display:none !important; }
    nav[aria-label="Sidebar"] ul { display:none !important; }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.subheader("Menu")
    st.write("If your full accordion groups are missing, re-apply the ALL-IN-ONE ZIP.")

st.title("Vega Cockpit • Google Sheets Integration")

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
