
import pandas as pd
from typing import Tuple

REQUIRED_COLS = [
    "Document","SKU","Type","Lot","ManufactureDate","ExpiryDate","FileLink","VerifiedBy","VerifiedOn","Notes"
]

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        df = pd.DataFrame(columns=REQUIRED_COLS)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = pd.NaT if c in ["ManufactureDate","ExpiryDate","VerifiedOn"] else ""
    # Keep consistent order
    return df[[c for c in REQUIRED_COLS if c in df.columns]]

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    for col in ["ManufactureDate","ExpiryDate","VerifiedOn"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def add_expiry_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure dates are datetimelike
    df = parse_dates(df)
    if df is None or df.empty:
        return df
    if "ExpiryDate" not in df.columns:
        df["ExpiryDate"] = pd.NaT
    today = pd.Timestamp("today").normalize()
    # Compute days to expiry safely
    df["DaysToExpiry"] = (df["ExpiryDate"] - today).dt.days
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
    if df is None or df.empty or "ExpiryStatus" not in df.columns:
        return 0,0,0,0
    expired = int((df["ExpiryStatus"] == "expired").sum())
    due30 = int((df["ExpiryStatus"] == "due in 30").sum())
    due60 = int((df["ExpiryStatus"] == "due in 60").sum())
    due90 = int((df["ExpiryStatus"] == "due in 90").sum())
    return expired, due30, due60, due90
