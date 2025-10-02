
from __future__ import annotations
import os, json, time, traceback, pandas as pd
from datetime import datetime, timedelta
from utils.sp_config import CONFIG
from integrations import sp_non_ads as sp

STATUS_PATH = os.environ.get("ETL_STATUS_PATH", "/tmp/etl_status.json")

def _write_status(status: dict):
    try:
        with open(STATUS_PATH, "w") as f:
            json.dump(status, f)
    except Exception:
        pass

def status():
    if not os.path.exists(STATUS_PATH):
        return {}
    try:
        with open(STATUS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def run_job(name: str, fn, *args, **kwargs):
    started = datetime.utcnow().isoformat()
    try:
        result = fn(*args, **kwargs)
        s = {"job": name, "status": "ok", "started": started, "ended": datetime.utcnow().isoformat()}
    except Exception as e:
        s = {"job": name, "status": "error", "started": started, "ended": datetime.utcnow().isoformat(),
             "error": str(e), "trace": traceback.format_exc()}
    _write_status(s)
    return s

# ---- Actual tasks ----
def refresh_orders_inventory_finances(days_back:int=30):
    orders = sp.list_orders(days_back=days_back)
    inv = sp.list_inventory()
    fin = sp.list_finances(days_back=days_back)
    # For now, write to /tmp CSVs or to Sheets later
    outdir = os.environ.get("ETL_OUT_DIR", "/tmp")
    os.makedirs(outdir, exist_ok=True)
    orders.to_csv(os.path.join(outdir, "orders.csv"), index=False)
    inv.to_csv(os.path.join(outdir, "inventory.csv"), index=False)
    fin.to_csv(os.path.join(outdir, "finances.csv"), index=False)
    return {"orders": len(orders), "inventory": len(inv), "finances": len(fin)}

def monthly_profitability_rollup():
    # A placeholder: later join Finance + Ads (when Ads API is ready). For now, summarize finances.csv
    outdir = os.environ.get("ETL_OUT_DIR", "/tmp")
    fin_path = os.path.join(outdir, "finances.csv")
    if not os.path.exists(fin_path):
        return {"rows": 0}
    df = pd.read_csv(fin_path)
    if df.empty or "date" not in df.columns:
        return {"rows": len(df)}
    df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").astype(str)
    roll = df.groupby(["month","sku"], as_index=False).agg(revenue=("revenue","sum"), fees=("fees","sum"), other=("other","sum"))
    roll.to_csv(os.path.join(outdir, "profitability_monthly.csv"), index=False)
    return {"rows": len(roll)}

if __name__ == "__main__":
    print(run_job("refresh_orders_inventory_finances", refresh_orders_inventory_finances))
    print(run_job("monthly_profitability_rollup", monthly_profitability_rollup))
