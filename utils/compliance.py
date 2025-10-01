import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple

REQUIRED_COLS = [
    "Document","SKU","Type","Lot","ManufactureDate","ExpiryDate","FileLink","VerifiedBy","VerifiedOn","Notes"
]

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = "" if c not in ["ManufactureDate","ExpiryDate","VerifiedOn"] else pd.NaT
    return df[REQUIRED_COLS]

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["ManufactureDate","ExpiryDate","VerifiedOn"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def add_expiry_metrics(df: pd.DataFrame, today: datetime = None) -> pd.DataFrame:
    if today is None:
        today = datetime.utcnow().date()
    df["DaysToExpiry"] = (pd.to_datetime(df["ExpiryDate"]).dt.date - today).dt.days
    def status(d):
        if pd.isna(d):
            return "unknown"
        if d < 0:
            return "expired"
        if d <= 30:
            return "due in 30"
        if d <= 60:
            return "due in 60"
        if d <= 90:
            return "due in 90"
        return "ok"
    df["ExpiryStatus"] = df["DaysToExpiry"].apply(status)
    return df

def kpi_counts(df: pd.DataFrame) -> Tuple[int,int,int,int]:
    expired = int((df["ExpiryStatus"] == "expired").sum())
    due30 = int((df["ExpiryStatus"] == "due in 30").sum())
    due60 = int((df["ExpiryStatus"] == "due in 60").sum())
    due90 = int((df["ExpiryStatus"] == "due in 90").sum())
    return expired, due30, due60, due90

def add_expiry_metrics(df):
    import pandas as pd
    if df is None or df.empty:
        return df
    if 'expiryDate' in df.columns:
        df['expiryDate'] = pd.to_datetime(df['expiryDate'], errors='coerce')
    today = pd.Timestamp('today').normalize()
    if 'expiryDate' in df.columns:
        df['daysToExpiry'] = (df['expiryDate'] - today).dt.days
    else:
        df['daysToExpiry'] = pd.NA
    return df
