import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional

# Optional: Google Sheets support if creds are present
GSPREAD_AVAILABLE = False
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except Exception:
    GSPREAD_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]

def _get_sa_credentials():
    """Load service account credentials from st.secrets['gsheets_credentials'] (JSON string)."""
    creds_blob = st.secrets.get("gsheets_credentials", "")
    if not creds_blob:
        return None
    try:
        if isinstance(creds_blob, dict):
            info = creds_blob
        else:
            info = json.loads(creds_blob)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    except Exception as e:
        st.warning(f"Google Sheets credentials could not be loaded: {e}")
        return None

def get_data_sources():
    keys = [
        "sp_api_refresh_token", "sp_api_client_id", "sp_api_client_secret", "sp_api_role_arn",
        "gsheets_credentials", "gsheets_product_sheet_id", "gsheets_ppc_sheet_id"
    ]
    present = {k: ("✓" if st.secrets.get(k) else "—") for k in keys}
    present["gspread_lib"] = "✓" if GSPREAD_AVAILABLE else "—"
    return present

@st.cache_data(ttl=300)
def load_sheet(sheet_id: str, worksheet_name: Optional[str] = None) -> pd.DataFrame:
    """Load a Google Sheet by file ID and optional worksheet name. Falls back to sample data."""
    if not sheet_id:
        kind = worksheet_name or "sheet"
        return load_sample_df(kind)
    if not GSPREAD_AVAILABLE:
        st.info("gspread not installed; using sample data")
        return load_sample_df(worksheet_name or "sheet")
    creds = _get_sa_credentials()
    if not creds:
        st.info("No gsheets_credentials in secrets; using sample data")
        return load_sample_df(worksheet_name or "sheet")
    try:
        client = gspread.authorize(creds)
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name) if worksheet_name else sh.sheet1
        rows = ws.get_all_records()
        df = pd.DataFrame(rows)
        return df if not df.empty else load_sample_df(worksheet_name or "sheet")
    except Exception as e:
        st.warning(f"Sheets read failed ({worksheet_name or 'sheet1'}): {e}")
        return load_sample_df(worksheet_name or "sheet")

def load_sample_df(kind: str = "sheet") -> pd.DataFrame:
    if "ppc" in kind.lower():
        return pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=14),
            "Campaign": ["Auto"]*7 + ["Exact"]*7,
            "Impressions": [10000,12500,9800,11700,10900,13200,12800, 15000,14100,16200,15800,14900,16700,17200],
            "Clicks": [300,320,280,305,295,345,330, 400,395,420,415,405,430,445],
            "Spend": [120,132,118,125,121,142,139, 210,205,219,214,209,223,229],
            "Orders": [25,26,23,24,24,28,27, 36,34,38,37,35,39,41],
            "ACoS%": [40,41,38,39,40,41,42, 33,32,31,32,31,30,29],
            "ROAS": [2.5,2.4,2.6,2.6,2.5,2.4,2.4, 3.0,3.1,3.2,3.1,3.2,3.3,3.4],
        })
    elif "product" in kind.lower():
        return pd.DataFrame({
            "ASIN": ["B00NOPAL01","B00MANGO01","B00NOPAL02"],
            "SKU": ["NOPAL-120","MANGO-120","NOPAL-240"],
            "Title": ["Nopal Cactus 120ct","Mangosteen Pericarp 120ct","Nopal Cactus 240ct"],
            "Sessions": [1500, 900, 600],
            "CVR%": [6.2, 4.9, 5.1],
            "Units": [93, 44, 31],
            "Price": [24.95, 29.95, 39.95],
            "Inventory": [420, 180, 95],
            "Days of Cover": [28, 19, 12],
            "Stars": [4.6, 4.4, 4.5],
            "Reviews": [812, 365, 145],
            "Suppressed?": [False, False, False]
        })
    elif "finance" in kind.lower():
        return pd.DataFrame({
            "Month": pd.period_range("2025-01", periods=8, freq="M").astype(str),
            "Revenue": [32000, 34500, 33800, 36100, 37200, 39500, 40200, 41800],
            "COGS": [12800, 13500, 13200, 14000, 14600, 15400, 15600, 16000],
            "Fees": [6400, 6900, 6700, 7000, 7200, 7600, 7700, 8000],
            "Ad Spend": [5200, 5400, 5600, 5900, 6000, 6200, 6400, 6600]
        })
    else:
        return pd.DataFrame({"Field": ["example"], "Value": ["placeholder"]})
