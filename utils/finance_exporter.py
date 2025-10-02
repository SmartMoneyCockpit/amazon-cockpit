
from __future__ import annotations
import pandas as pd
from utils.sheets_writer import write_df

def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Ensure columns exist
    for col in ["revenue","fees","other"]:
        if col not in df.columns:
            df[col] = 0.0
    df["net"] = df["revenue"].fillna(0) - df["fees"].fillna(0) - df["other"].fillna(0)
    # Group by month (and SKU optional)
    if "month" not in df.columns:
        df["month"] = ""
    summary = (
        df.groupby("month", as_index=False)
          .agg(revenue=("revenue","sum"), fees=("fees","sum"), other=("other","sum"), net=("net","sum"))
          .sort_values("month")
    )
    return summary

def export_summary_to_sheet(df: pd.DataFrame, tab_name: str = "finance_summary") -> str:
    summary = build_summary(df)
    return write_df(tab_name, summary, clear=True)
