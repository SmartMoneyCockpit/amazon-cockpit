import os
import streamlit as st
from infra.sheets_client import SheetsClient

st.set_page_config(
    page_title="Vega Cockpit - Google Sheets",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display:none !important; }
    nav[aria-label="Sidebar"] ul { display:none !important; }
    </style>
    """, unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Menu")
    st.write("Accordion intact — defaults preloaded.")

st.title("Vega Cockpit • Google Sheets Integration")
st.subheader("Settings preview")

def _get(k, d=None):
    try:
        return st.secrets.get(k, d)
    except Exception:
        return os.getenv(k.upper(), d)

def _fmt(v):
    if v is None or v == "":
        return "—"
    return str(v)

try:
    sc = SheetsClient()
    rows = sc.read_table("Settings")
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("No rows yet in 'Settings'.")
except Exception:
    import pandas as pd
    data = [
        {"key": "timezone", "value": _fmt(_get("timezone", "America/Mazatlan"))},
        {"key": "base_currency", "value": _fmt(_get("base_currency", "USD"))},
        {"key": "report_start_date", "value": _fmt(_get("report_start_date", "2025-10-02"))},
        {"key": "ads_enabled", "value": _fmt(_get("ads_enabled", True))},
        {"key": "auto_snapshot_pdf", "value": _fmt(_get("auto_snapshot_pdf", True))},
    ]
    st.caption("Defaults loaded from bundle; update your secrets/env to override.")
    st.dataframe(pd.DataFrame(data), use_container_width=True)
