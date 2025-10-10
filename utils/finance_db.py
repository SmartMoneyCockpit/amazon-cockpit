# utils/finance_db.py
from __future__ import annotations
import pandas as pd
from typing import Tuple
from utils.api_client import finance_summary, finance_daily

def fetch_finance_snapshot(limit: int = 60) -> pd.DataFrame:
    ok, daily = finance_daily(limit=limit)
    if not ok or not isinstance(daily, list):
        return pd.DataFrame(columns=["Date","Units","Revenue","COGS","Fees","AdSpend","NetProfit"])
    df = pd.DataFrame(daily)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["NetProfit"] = (df.get("revenue", 0) - df.get("cogs", 0) - df.get("fees", 0) - df.get("ad_spend", 0))
    # pretty columns
    out = df.rename(columns={
        "date":"Date","units":"Units","revenue":"Revenue","cogs":"COGS","fees":"Fees","ad_spend":"AdSpend"
    })
    cols = ["Date","Units","Revenue","COGS","Fees","AdSpend","NetProfit"]
    for c in cols:
        if c not in out.columns:
            out[c] = 0
    return out[cols]

def kpis(_df: pd.DataFrame) -> Tuple[float, float, float, float]:
    ok, s = finance_summary()
    if ok and isinstance(s, dict):
        rev = float(s.get("revenue", 0.0))
        gp  = float(s.get("gross_profit", 0.0))
        np  = float(s.get("net_profit", 0.0))
        acos = float(s.get("acos_pct", 0.0))
        return rev, gp, np, acos
    # fallback if summary call fails
    rev = float(_df.get("Revenue", pd.Series()).sum()) if "Revenue" in _df.columns else 0.0
    gp  = float((_df.get("Revenue",0) - _df.get("COGS",0) - _df.get("Fees",0)).sum()) if not _df.empty else 0.0
    np  = float((_df.get("Revenue",0) - _df.get("COGS",0) - _df.get("Fees",0) - _df.get("AdSpend",0)).sum()) if not _df.empty else 0.0
    acos = float((_df.get("AdSpend",0).sum() / rev) * 100.0) if rev > 0 else 0.0
    return rev, gp, np, acos
