from __future__ import annotations
import os, pathlib, datetime as dt
from infra.sheets_client import SheetsClient
import pandas as pd

def export_daily_snapshot(out_dir: str = "snapshots", sheet_name: str = "Settings") -> str:
    d = dt.date.today().isoformat()
    out = pathlib.Path(out_dir) / d
    out.mkdir(parents=True, exist_ok=True)
    try:
        sc = SheetsClient()
        rows = sc.read_table(sheet_name)
        df = pd.DataFrame(rows)
    except Exception as e:
        df = pd.DataFrame([{"error": str(e)}])
    csv_path = out / f"{sheet_name}.csv"
    df.to_csv(csv_path, index=False)
    return str(out)
