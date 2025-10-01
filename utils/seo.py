import pandas as pd
import streamlit as st
from typing import Tuple

from utils.data import load_sheet, load_sample_df

def load_keyword_index_df() -> pd.DataFrame:
    sheet_id = st.secrets.get("gsheets_keywords_sheet_id", "")
    if sheet_id:
        return load_sheet(sheet_id, "keywords")
    # Sample structure
    return pd.DataFrame({
        "ASIN": ["B00NOPAL01","B00MANGO01","B00NOPAL02"],
        "Keyword": ["nopal cactus","mangosteen pericarp","nopal capsules"],
        "MatchType": ["Exact","Exact","Phrase"],
        "Indexed?": [True, True, False],
        "Rank": [7, 12, None],
        "Priority": ["High","High","High"]
    })

def load_competitors_df() -> pd.DataFrame:
    sheet_id = st.secrets.get("gsheets_competitors_sheet_id", "")
    if sheet_id:
        return load_sheet(sheet_id, "competitors")
    return pd.DataFrame({
        "CompetitorASIN": ["C001","C002","C003"],
        "Title": ["Brand X Nopal 120ct","Brand Y Mangosteen","Brand Z Nopal 240ct"],
        "Price": [22.95, 27.95, 37.95],
        "Stars": [4.4, 4.2, 4.5],
        "Reviews": [421, 310, 256],
        "APlus?": [True, False, True],
        "MainImageQuality": ["Good","Fair","Good"]
    })

def indexing_kpis(df: pd.DataFrame) -> Tuple[int,int,int]:
    total = len(df.index)
    indexed = int(df["Indexed?"].fillna(False).sum()) if "Indexed?" in df.columns else 0
    missing = total - indexed
    return total, indexed, missing

def deindexed_critical(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if "Priority" in d.columns:
        d = d[d["Priority"].str.lower() == "high"]
    if "Indexed?" in d.columns:
        d = d[d["Indexed?"] != True]
    return d
