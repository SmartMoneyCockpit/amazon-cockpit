
from __future__ import annotations
import os
import pandas as pd
try:
    from utils import sheets_bridge as SB  # must expose write_tab(name, df)
    HAVE_SB = True
except Exception:
    SB = None
    HAVE_SB = False

OUT_DIR = os.environ.get("ETL_OUT_DIR", "/tmp")

def write_df(tab_name: str, df: pd.DataFrame, clear: bool = True) -> str:
    if df is None:
        return "no_df"
    if HAVE_SB and hasattr(SB, "write_tab"):
        try:
            SB.write_tab(tab_name, df, clear=clear)  # type: ignore
            return f"sheet:{tab_name}:{len(df)}"
        except Exception:
            pass
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{tab_name}.csv")
    df.to_csv(path, index=False)
    return f"csv:{path}:{len(df)}"
