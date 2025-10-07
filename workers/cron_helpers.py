
from __future__ import annotations
import sys, datetime as dt, pandas as pd
from utils.logs import log_job
from infra.sheets_client import SheetsClient
def _try_import_snapshot():
    try:
        from snapshot import export_daily_snapshot; return export_daily_snapshot
    except Exception: return None
def _try_import_exporters():
    try:
        from utils.exporters import export_finance_monthly; return export_finance_monthly
    except Exception: return None
def read_finances_df():
    try: sc=SheetsClient(); rows=sc.read_table("Finances"); return pd.DataFrame(rows)
    except Exception: return pd.DataFrame(columns=["date","gmv","acos","tacos","refund_rate"])
def run_snapshot():
    export=_try_import_snapshot()
    if not export: log_job("daily_snapshot","error","snapshot module not found"); return 2
    try: out=export(); log_job("daily_snapshot","ok", f"exported to {out}"); print(f"[daily_snapshot] OK -> {out}"); return 0
    except Exception as e: log_job("daily_snapshot","error", f"{e!r}"); print(f"[daily_snapshot] ERROR -> {e!r}"); return 1
def run_monthly_export(year=None, month=None):
    export_finance_monthly=_try_import_exporters()
    if not export_finance_monthly: log_job("monthly_finance_export","error","exporter not found"); return 2
    today=dt.date.today()
    if year is None or month is None:
        y=today.year; m=today.month-1 or 12
        if today.month==1: y=today.year-1
    else: y,m=int(year),int(month)
    try:
        df=read_finances_df(); csv_path,pdf_path=export_finance_monthly(df,y,m); detail=f"CSV {csv_path}"+(f"; PDF {pdf_path}" if pdf_path else "")
        log_job("monthly_finance_export","ok", detail, {"year":y,"month":m}); print(f"[monthly_finance_export] OK -> {detail}"); return 0
    except Exception as e: log_job("monthly_finance_export","error", f"{e!r}", {"year":y,"month":m}); print(f"[monthly_finance_export] ERROR -> {e!r}"); return 1
def main(argv: list[str])->int:
    if len(argv)<2: print("Usage: python -m workers.cron_helpers <snapshot|monthly> [YYYY MM]"); return 64
    cmd=argv[1].lower()
    if cmd=="snapshot": return run_snapshot()
    if cmd=="monthly": y=int(argv[2]) if len(argv)>2 else None; m=int(argv[3]) if len(argv)>3 else None; return run_monthly_export(y,m)
    print(f"Unknown command: {cmd}"); return 64
if __name__=="__main__": raise SystemExit(main(sys.argv))
