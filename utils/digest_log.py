"""
Daily Digest metadata logger.
Appends a 1-row summary (date + KPIs + alert counts) to a Google Sheet.

Secrets expected:
- gsheets_digest_log_sheet_id  (target Google Sheet file ID)
- gsheets_credentials          (service account JSON; already used elsewhere)

Depends on:
- utils/gsheets_write.append_df
- utils.finance (for KPIs)
- utils.data.load_sample_df (for product health)
"""
from datetime import datetime
import pandas as pd
import streamlit as st

from utils.finance import load_finance_df, compute_profitability, kpis as finance_kpis
from utils.data import load_sample_df
from utils.alerts_archive import alerts_buffer_to_df
from utils.gsheets_write import append_df

def compute_kpis() -> dict:
    # Finance KPIs (period aggregate)
    f_raw = load_finance_df()
    f_df = compute_profitability(f_raw)
    rev, gp, np, acos = finance_kpis(f_df)

    # Product health
    p_df = load_sample_df("product")
    low_doc = int((p_df["Days of Cover"] < 10).sum())
    suppressed = int((p_df.get("Suppressed?", False) == True).sum()) if "Suppressed?" in p_df.columns else 0
    avg_stars = float(p_df["Stars"].mean()) if "Stars" in p_df.columns and not p_df.empty else 0.0

    # Alerts counts
    a_df = alerts_buffer_to_df(limit=None)
    total_alerts = int(len(a_df.index)) if not a_df.empty else 0
    crit = int((a_df["severity"]=="crit").sum()) if "severity" in a_df.columns else 0
    warn = int((a_df["severity"]=="warn").sum()) if "severity" in a_df.columns else 0
    info = int((a_df["severity"]=="info").sum()) if "severity" in a_df.columns else 0

    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "revenue": float(rev),
        "gross_profit": float(gp),
        "net_profit": float(np),
        "acos_pct": float(acos),
        "asins": int(len(p_df.index)),
        "low_cover": int(low_doc),
        "suppressed": int(suppressed),
        "avg_stars": float(avg_stars),
        "alerts_total": total_alerts,
        "alerts_crit": crit,
        "alerts_warn": warn,
        "alerts_info": info
    }

def append_digest_metadata(sheet_id: str, worksheet: str = "daily_digest_log") -> int:
    rec = compute_kpis()
    df = pd.DataFrame([rec])
    return append_df(sheet_id, worksheet, df)
