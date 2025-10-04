from __future__ import annotations
import datetime as dt
from typing import Dict, Any, List, Tuple
import pandas as pd

# Expected "Finances" sheet minimal columns:
# date (YYYY-MM-DD), gmv (float), acos (float 0-1 or 0-100), tacos (float), refund_rate (float)

def _coerce_percent(x):
    if x is None or x == "":
        return None
    try:
        x = float(x)
    except Exception:
        return None
    # Accept values like 0.12 or 12 -> both mean 12%
    return x if x <= 1.5 else x / 100.0

def _as_date(s):
    try:
        return pd.to_datetime(s).date()
    except Exception:
        return None

def build_kpis(finances_rows: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], pd.DataFrame]:
    if not finances_rows:
        # Demo fallback with synthetic last-30d values
        today = dt.date.today()
        days = pd.date_range(end=today, periods=30, freq="D")
        demo = pd.DataFrame({
            "date": days,
            "gmv": [1000 + i*5 for i in range(len(days))],
            "acos": [0.22]*len(days),
            "tacos": [0.28]*len(days),
            "refund_rate": [0.015]*len(days),
        })
        kpis = {
            "gmv_30d": float(demo["gmv"].tail(30).sum()),
            "acos": float(demo["acos"].iloc[-1]),
            "tacos": float(demo["tacos"].iloc[-1]),
            "refund_rate": float(demo["refund_rate"].iloc[-1]),
        }
        return kpis, demo

    df = pd.DataFrame(finances_rows).copy()
    # Normalize columns
    rename_map = {c: c.lower().strip() for c in df.columns}
    df.rename(columns=rename_map, inplace=True)
    # Coerce types
    if "date" in df.columns:
        df["date"] = df["date"].apply(_as_date)
    for c in ("gmv", "acos", "tacos", "refund_rate"):
        if c in df.columns:
            if c in ("acos","tacos","refund_rate"):
                df[c] = df[c].apply(_coerce_percent)
            else:
                df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")
    # Compute KPIs
    last_30 = df.tail(30)
    kpis = {
        "gmv_30d": float(last_30["gmv"].sum()) if "gmv" in df.columns else 0.0,
        "acos": float(df["acos"].iloc[-1]) if "acos" in df.columns else None,
        "tacos": float(df["tacos"].iloc[-1]) if "tacos" in df.columns else None,
        "refund_rate": float(df["refund_rate"].iloc[-1]) if "refund_rate" in df.columns else None,
    }
    return kpis, df
