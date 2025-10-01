"""
Google Sheets write-back helper (append rows) using gspread + service account.
Reads credentials from Streamlit secrets: `gsheets_credentials` (JSON) as in prior steps.
"""

import json
from typing import Optional, List
import pandas as pd
import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except Exception:
    GSPREAD_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def _creds():
    blob = st.secrets.get("gsheets_credentials", "")
    if not blob:
        return None
    try:
        info = blob if isinstance(blob, dict) else json.loads(blob)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception as e:
        st.error(f"gsheets credentials parse error: {e}")
        return None

def ensure_worksheet(sh, title: str):
    try:
        return sh.worksheet(title)
    except Exception:
        return sh.add_worksheet(title=title, rows=1000, cols=26)

def append_df(sheet_id: str, worksheet_title: str, df: pd.DataFrame) -> int:
    """
    Append a DataFrame to the end of a worksheet. Returns number of rows appended.
    Creates the worksheet if missing and writes headers if empty.
    """
    if not GSPREAD_AVAILABLE:
        st.error("gspread not installed; add gspread and google-auth to requirements.txt")
        return 0
    creds = _creds()
    if not creds:
        st.error("Missing gsheets_credentials in secrets")
        return 0
    if df is None or df.empty:
        st.info("Nothing to append (empty DataFrame).")
        return 0

    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    ws = ensure_worksheet(sh, worksheet_title)

    # Determine if worksheet is empty: get all values (first row) safely
    values = ws.get_all_values()
    write_header = len(values) == 0
    # If headers exist but mismatch, we still write rows in column order of df
    rows = [df.columns.tolist()] + df.astype(str).values.tolist() if write_header else df.astype(str).values.tolist()
    ws.append_rows(rows, value_input_option="USER_ENTERED")
    return len(df.index)
