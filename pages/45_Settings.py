
import streamlit as st
import pandas as pd
from utils.settings_loader import load_settings
from infra.sheets_client import SheetsClient
from utils.logs import log_job
from utils.credentials_check import test_sheets, test_sendgrid

st.set_page_config(page_title="Settings v2.0", layout="wide")
st.title("Settings — Admin Console (v2.0)")

# Load merged values + sources
values, sources, last_sync = load_settings()

def _badge(src: str) -> str:
    color = {"sheets": "#16a34a", "secrets": "#f59e0b", "env": "#3b82f6", "default": "#6b7280"}.get(src, "#6b7280")
    label = {"sheets": "Sheets", "secrets": "Secrets", "env": "Env", "default": "Default"}.get(src, src.title())
    return f"<span style='padding:.2rem .5rem;border-radius:999px;background:{color};color:#fff;font-size:.75rem;'>{label}</span>"

# Source-of-truth badges
st.caption(f"Last sync: {last_sync}")
csrc1, csrc2 = st.columns(2)
with csrc1:
    st.markdown(f"**Timezone**: `{values['timezone']}`  " + _badge(sources['timezone']), unsafe_allow_html=True)
    st.markdown(f"**Base currency**: `{values['base_currency']}`  " + _badge(sources['base_currency']), unsafe_allow_html=True)
    st.markdown(f"**Report start date**: `{values['report_start_date']}`  " + _badge(sources['report_start_date']), unsafe_allow_html=True)
with csrc2:
    st.markdown(f"**Ads enabled**: `{values['ads_enabled']}`  " + _badge(sources['ads_enabled']), unsafe_allow_html=True)
    st.markdown(f"**Auto Snapshot PDF**: `{values['auto_snapshot_pdf']}`  " + _badge(sources['auto_snapshot_pdf']), unsafe_allow_html=True)

st.divider()
st.subheader("Edit & Save to Google Sheets ('Settings' worksheet)")

# Editable inputs (prefilled with merged values)
ec1, ec2 = st.columns(2)
with ec1:
    tz = st.text_input("Timezone", value=str(values.get("timezone","America/Los_Angeles")))
    cur = st.text_input("Base currency", value=str(values.get("base_currency","USD")), max_chars=3)
    rsd = st.text_input("Report start date (YYYY-MM-DD)", value=str(values.get("report_start_date","2025-01-01")))
with ec2:
    ads = st.toggle("Ads enabled", value=bool(values.get("ads_enabled", True)))
    snap = st.toggle("Auto Snapshot PDF", value=bool(values.get("auto_snapshot_pdf", True)))

save_col, test_col1, test_col2 = st.columns([1,1,1])
with save_col:
    if st.button("Save to Sheets"):
        try:
            sc = SheetsClient()
            rows = [
                {"key": "timezone", "value": tz},
                {"key": "base_currency", "value": cur.upper()},
                {"key": "report_start_date", "value": rsd},
                {"key": "ads_enabled", "value": ads},
                {"key": "auto_snapshot_pdf", "value": snap},
            ]
            df = pd.DataFrame(rows)
            sc.write_table("Settings", df, clear=True)
            log_job("settings_admin_save", "ok", "Settings saved to 'Settings' worksheet")
            st.success("Saved to Google Sheets.")
        except Exception as e:
            try:
                log_job("settings_admin_save", "error", str(e))
            except Exception:
                pass
            st.error(f"Save failed: {e}")

with test_col1:
    if st.button("Test Google Sheets"):
        ok, msg = test_sheets()
        st.success(msg) if ok else st.error(msg)

with test_col2:
    if st.button("Test SendGrid (keys only)"):
        ok, msg = test_sendgrid()
        st.success(msg) if ok else st.error(msg)

st.divider()
st.caption("This page is menu-safe and reuses your existing Settings slot. Values are saved only to the 'Settings' Google Sheet, not to secrets/env.")
