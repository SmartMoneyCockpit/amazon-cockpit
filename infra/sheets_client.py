from __future__ import annotations
import os, json
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential

def _read_service_account_creds():
    # Prefer secrets, then env JSON, then file path
    try:
        if "gcp_service_account_json" in st.secrets:
            info = st.secrets["gcp_service_account_json"]
            if isinstance(info, (str, bytes)):
                info = json.loads(info)
            return Credentials.from_service_account_info(info, scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ])
    except Exception:
        pass

    env_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if env_json:
        info = json.loads(env_json)
        return Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])

    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "gcp_service_account.json"
    if os.path.exists(path):
        return Credentials.from_service_account_file(path, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])

    raise FileNotFoundError("No GCP credentials found. Provide st.secrets['gcp_service_account_json'] or env GCP_SERVICE_ACCOUNT_JSON or a GOOGLE_APPLICATION_CREDENTIALS path.")

def _get_sheet_key():
    key = None
    try:
        key = st.secrets.get("sheets_key", None)
    except Exception:
        pass
    key = key or os.getenv("SHEETS_KEY") or os.getenv("GOOGLE_SHEET_KEY")
    if not key:
        raise RuntimeError("Missing Sheets key. Set st.secrets['sheets_key'] or env SHEETS_KEY.")
    return key

class SheetsClient:
    def __init__(self):
        creds = _read_service_account_creds()
        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open_by_key(_get_sheet_key())

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, min=0.5, max=6))
    def read_table(self, sheet_name: str):
        ws = self.sh.worksheet(sheet_name)
        rows = ws.get_all_records()
        return rows

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=0.5, min=0.5, max=6))
    def write_table(self, sheet_name: str, rows, clear=False):
        try:
            ws = self.sh.worksheet(sheet_name)
        except Exception:
            ws = self.sh.add_worksheet(sheet_name, rows=100, cols=10)

        if clear:
            ws.clear()

        df = pd.DataFrame(rows)
        if df.empty:
            return

        ws.update([df.columns.tolist()] + df.values.tolist())
