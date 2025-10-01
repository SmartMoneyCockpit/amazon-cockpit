import os
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def get_data_sources():
    """Return a dict of configured data sources/secrets (redacted)."""
    keys = ["sp_api_refresh_token", "sp_api_client_id", "sp_api_client_secret", "sp_api_role_arn",
            "gsheets_credentials", "gsheets_product_sheet_id", "gsheets_ppc_sheet_id"]
    present = {k: ("✓" if st.secrets.get(k) else "—") for k in keys}
    return present

@st.cache_data(ttl=300)
def load_sheet(sheet_id: str, sheet_name: str = None) -> pd.DataFrame:
    """Placeholder: load from Google Sheets. For now returns a sample DF if sheet_id empty."""
    if not sheet_id:
        return load_sample_df(sheet_name or "sheet")
    # TODO: implement gspread/Google API read here when credentials are added.
    return load_sample_df(sheet_name or "sheet")

def load_sample_df(kind: str = "sheet") -> pd.DataFrame:
    if kind.lower().startswith("ppc"):
        return pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=14),
            "Campaign": ["Auto"]*7 + ["Exact"]*7,
            "Impressions": [10_000,12_500,9_800,11_700,10_900,13_200,12_800, 15_000,14_100,16_200,15_800,14_900,16_700,17_200],
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
        return pd.DataFrame({
            "Field": ["example"],
            "Value": ["placeholder"]
        })
