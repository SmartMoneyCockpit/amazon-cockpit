
from __future__ import annotations
import pandas as pd

def read_tab(name: str) -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB
        df = SB.read_tab(name)
        if isinstance(df, pd.DataFrame):
            return df
    except Exception:
        pass
    return pd.DataFrame()

def derive_finance(fin: pd.DataFrame) -> pd.DataFrame:
    if fin.empty: 
        return fin
    f = fin.copy()
    f.columns = [c.strip().lower() for c in f.columns]
    if "date" in f.columns and "month" not in f.columns:
        f["month"] = pd.to_datetime(f["date"], errors="coerce").dt.to_period("M").astype(str)
    for c in ["revenue","fees","other"]:
        if c not in f.columns: f[c] = 0.0
    f["net"] = f["revenue"] - f["fees"] - f["other"]
    return f

def count_severity(actions: pd.DataFrame):
    if actions.empty or "severity" not in actions.columns:
        return 0, 0, 0
    sev = actions["severity"].astype(str).str.lower()
    return int((sev=="red").sum()), int((sev=="yellow").sum()), int((sev=="green").sum())
