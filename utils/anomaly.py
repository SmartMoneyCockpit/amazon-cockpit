
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

def _zscore(series: pd.Series, window: int = 14) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    roll = x.rolling(window=window, min_periods=max(3, window//2))
    mu = roll.mean()
    sigma = roll.std(ddof=0)
    z = (x - mu) / sigma.replace(0, np.nan)
    return z

def detect_anomalies(df: pd.DataFrame,
                     cols: List[str] = ["gmv","acos","tacos","refund_rate"],
                     window: int = 14,
                     z_thresh: float = 2.0) -> Tuple[Dict[str, Any], pd.DataFrame]:
    if df is None or df.empty:
        return {c: False for c in cols}, pd.DataFrame()

    d = df.copy()
    for c in cols:
        if c in d.columns:
            z = _zscore(d[c], window=window)
            d[f"{c}_z"] = z
            d[f"{c}_anomaly"] = (z.abs() >= z_thresh)
        else:
            d[f"{c}_z"] = np.nan
            d[f"{c}_anomaly"] = False

    latest_flags = {}
    for c in cols:
        if f"{c}_anomaly" in d.columns and not d.empty:
            val = bool(d[f"{c}_anomaly"].iloc[-1])
        else:
            val = False
        latest_flags[c] = val

    return latest_flags, d
