import pandas as pd
import streamlit as st
from typing import Tuple

from utils.data import load_sheet, load_sample_df

FINANCE_WS_NAME = "finance"  # expected worksheet name

def load_finance_df() -> pd.DataFrame:
    """Load finance data from Google Sheets (if configured) or return a sample structure.
    Expected columns: Month, SKU, ASIN, Units, Revenue, COGS, Fees, AdSpend
    """
    sheet_id = st.secrets.get("gsheets_finance_sheet_id", "")
    if sheet_id:
        df = load_sheet(sheet_id, FINANCE_WS_NAME)
        return normalize_finance_df(df)
    # Sample
    df = pd.DataFrame({
        "Month": pd.period_range("2025-01", periods=8, freq="M").astype(str).tolist() * 3,
        "SKU": (["NOPAL-120"]*8) + (["MANGO-120"]*8) + (["NOPAL-240"]*8),
        "ASIN": (["B00NOPAL01"]*8) + (["B00MANGO01"]*8) + (["B00NOPAL02"]*8),
        "Units": [120,128,115,132,140,151,149,156, 80,82,79,85,88,91,93,95, 60,62,59,64,66,68,69,71],
        "Revenue": [2994,3120,2810,3250,3380,3520,3605,3720, 2396,2460,2380,2500,2590,2680,2750,2830, 2796,2860,2780,2900,3050,3120,3200,3300],
        "COGS":    [1200,1280,1150,1320,1400,1510,1490,1560,  960,  984,  948,  1000, 1030, 1060, 1100, 1120,  1200,1240,1180,1280,1320,1360,1380,1420],
        "Fees":    [640,  690,  670,  700,  720,  760,  770,  800,  520,  540,  560,  590,  600,  620,  640,  660,   620,  640,  650,  660,  680,  700,  710,  730],
        "AdSpend": [420,  430,  440,  460,  470,  490,  500,  520,  380,  390,  400,  420,  430,  440,  450,  460,   410,  420,  430,  440,  450,  460,  470,  480],
    })
    return normalize_finance_df(df)

def normalize_finance_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Month","SKU","ASIN","Units","Revenue","COGS","Fees","AdSpend"]
    for c in cols:
        if c not in df.columns:
            df[c] = 0 if c in ["Units","Revenue","COGS","Fees","AdSpend"] else ""
    df = df[cols].copy()
    # Ensure numeric
    for c in ["Units","Revenue","COGS","Fees","AdSpend"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    # Month as string yyyy-mm
    df["Month"] = df["Month"].astype(str)
    return df

def compute_profitability(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["GrossProfit"] = out["Revenue"] - out["COGS"] - out["Fees"]
    out["NetProfit"] = out["GrossProfit"] - out["AdSpend"]
    out["GrossMargin%"] = (out["GrossProfit"] / out["Revenue"]).replace([pd.NA, float("inf"), -float("inf")], 0) * 100
    out["NetMargin%"] = (out["NetProfit"] / out["Revenue"]).replace([pd.NA, float("inf"), -float("inf")], 0) * 100
    out["Acos%"] = (out["AdSpend"] / out["Revenue"]).replace([pd.NA, float("inf"), -float("inf")], 0) * 100
    out["RevPerUnit"] = (out["Revenue"] / out["Units"]).replace([pd.NA, float("inf"), -float("inf")], 0)
    out["COGSPerUnit"] = (out["COGS"] / out["Units"]).replace([pd.NA, float("inf"), -float("inf")], 0)
    out["FeesPerUnit"] = (out["Fees"] / out["Units"]).replace([pd.NA, float("inf"), -float("inf")], 0)
    out["AdPerUnit"] = (out["AdSpend"] / out["Units"]).replace([pd.NA, float("inf"), -float("inf")], 0)
    out["NetPerUnit"] = (out["NetProfit"] / out["Units"]).replace([pd.NA, float("inf"), -float("inf")], 0)
    return out

def kpis(summary: pd.DataFrame) -> Tuple[float, float, float, float]:
    rev = float(summary["Revenue"].sum())
    gp = float(summary["GrossProfit"].sum())
    np = float(summary["NetProfit"].sum())
    acos = float((summary["AdSpend"].sum() / max(rev, 1e-9)) * 100.0)
    return rev, gp, np, acos
