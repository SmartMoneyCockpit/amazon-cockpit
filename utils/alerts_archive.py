"""
Alerts History archiving utilities.
- Append current alerts buffer to Google Sheets (append-only)
- Export a daily PDF snapshot of alerts
Requires:
  - utils/gsheets_write.append_df
  - utils/export.simple_pdf_bytes
Secrets:
  - gsheets_alerts_history_sheet_id (Google Sheet file ID)
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from utils.export import simple_pdf_bytes, df_to_csv_bytes, df_to_xlsx_bytes
from utils.gsheets_write import append_df

def alerts_buffer_to_df(limit: int = None) -> pd.DataFrame:
    buf = st.session_state.get("alerts_buffer", [])
    df = pd.DataFrame(buf)
    if df.empty:
        df = pd.DataFrame(columns=["severity","message","source"])
    # Add timestamp if missing
    if "timestamp" not in df.columns:
        df.insert(0, "timestamp", datetime.utcnow().isoformat(timespec="seconds")+"Z")
    # Reorder columns for consistency
    cols = [c for c in ["timestamp","severity","source","message"] if c in df.columns] + [c for c in df.columns if c not in ["timestamp","severity","source","message"]]
    df = df[cols]
    if limit:
        df = df.tail(limit)
    return df

def export_alerts_pdf(title: str = "Alerts History Snapshot", limit: int = 200) -> bytes:
    df = alerts_buffer_to_df(limit=limit)
    return simple_pdf_bytes(title, df)

def export_alerts_csv(limit: int = 200) -> bytes:
    df = alerts_buffer_to_df(limit=limit)
    return df_to_csv_bytes(df)

def export_alerts_xlsx(limit: int = 200) -> bytes:
    df = alerts_buffer_to_df(limit=limit)
    return df_to_xlsx_bytes(df)

def append_alerts_to_sheet(sheet_id: str, worksheet_title: str = "alerts_history", limit: int = None) -> int:
    df = alerts_buffer_to_df(limit=limit)
    if df.empty:
        return 0
    return append_df(sheet_id, worksheet_title, df)
