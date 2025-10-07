
from __future__ import annotations
import pathlib, datetime as dt, pandas as pd
def _month_bounds(year:int, month:int):
    start=dt.date(year, month, 1)
    end=dt.date(year+1,1,1) if month==12 else dt.date(year,month+1,1)
    return start, end
def export_finance_monthly(df: pd.DataFrame, year:int, month:int, out_dir: str="snapshots"):
    out_base=pathlib.Path(out_dir)/f"{year:04d}-{month:02d}"; out_base.mkdir(parents=True, exist_ok=True)
    dfn=df.copy(); dfn.columns=[str(c).strip().lower() for c in dfn.columns]
    if "date" in dfn.columns: dfn["date"]=pd.to_datetime(dfn["date"],errors="coerce").dt.date
    start,end=_month_bounds(year, month)
    if "date" in dfn.columns: dfn=dfn[(dfn["date"]>=start)&(dfn["date"]<end)]
    csv_path=out_base/"finance_monthly.csv"; dfn.to_csv(csv_path, index=False)
    return csv_path.as_posix(), None
