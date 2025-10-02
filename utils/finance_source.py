
from __future__ import annotations
import os
import pandas as pd

OUT_DIR = os.environ.get("ETL_OUT_DIR", "/tmp")

# Try Google Sheet first, fall back to /tmp CSV
def read_profitability_monthly() -> pd.DataFrame:
    try:
        from utils import sheets_bridge as SB  # expects read_tab(name)
        df = SB.read_tab("profitability_monthly")
        if isinstance(df, pd.DataFrame):
            return df
    except Exception:
        pass

    path = os.path.join(OUT_DIR, "profitability_monthly.csv")
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            pass

    return pd.DataFrame(columns=["month","sku","revenue","fees","other"])
