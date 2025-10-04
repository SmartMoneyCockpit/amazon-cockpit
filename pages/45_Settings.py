
import streamlit as st
import pandas as pd
from utils.settings_loader import load_settings
from infra.sheets_client import SheetsClient
from utils.logs import log_job

st.set_page_config(page_title="Settings v1.1", layout="wide")
st.title("Settings")

values, sources, last_sync = load_settings()

def _badge(src: str) -> str:
    color = {"sheets": "#16a34a", "secrets": "#f59e0b", "env": "#3b82f6", "default": "#6b7280"}.get(src, "#6b7280")
    label = {"sheets": "Sheets", "secrets": "Secrets", "env": "Env", "default": "Default"}.get(src, src.title())
    return f"<span style='padding:.2rem .5rem;border-radius:999px;background:{color};color:#fff;font-size:.75rem;'>{label}</span>"

cols = st.columns(2)
with cols[0]:
    st.markdown(f"**Timezone**: `{values['timezone']}`  " + _badge(sources["timezone"]), unsafe_allow_html=True)
    st.markdown(f"**Base currency**: `{values['base_currency']}`  " + _badge(sources['base_currency']), unsafe_allow_html=True)
    st.markdown(f"**Report start date**: `{values['report_start_date']}`  " + _badge(sources['report_start_date']), unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"**Ads enabled**: `{values['ads_enabled']}`  " + _badge(sources['ads_enabled']), unsafe_allow_html=True)
    st.markdown(f"**Auto Snapshot PDF**: `{values['auto_snapshot_pdf']}`  " + _badge(sources['auto_snapshot_pdf']), unsafe_allow_html=True)

st.caption(f"Last sync: {last_sync}")

st.divider()
st.subheader("Write Sample Settings to Google Sheets")
st.caption("Creates/overwrites the 'Settings' worksheet with sample rows (key/value/source).")

if st.button("Write Sample Settings"):
    try:
        sc = SheetsClient()
        rows = [
            {"key": "timezone", "value": values.get("timezone", "America/Los_Angeles"), "source": "sample"},
            {"key": "base_currency", "value": values.get("base_currency", "USD"), "source": "sample"},
            {"key": "report_start_date", "value": values.get("report_start_date", "2025-01-01"), "source": "sample"},
            {"key": "ads_enabled", "value": values.get("ads_enabled", True), "source": "sample"},
            {"key": "auto_snapshot_pdf", "value": values.get("auto_snapshot_pdf", True), "source": "sample"},
        ]
        df = pd.DataFrame(rows)
        sc.write_table("Settings", df, clear=True)
        log_job("write_settings_sample", "ok", "Wrote sample rows to 'Settings'")
        st.success("Sample settings written to Google Sheets.")
    except Exception as e:
        try:
            log_job("write_settings_sample", "error", str(e))
        except Exception:
            pass
        st.error(f"Failed to write sample settings: {e}")
