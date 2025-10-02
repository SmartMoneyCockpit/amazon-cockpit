
from __future__ import annotations
import os, json, traceback, pandas as pd
from datetime import datetime, timedelta
from utils.sp_config import CONFIG
from integrations import sp_non_ads as sp
from utils.sheets_writer import write_df

STATUS_PATH = os.environ.get("ETL_STATUS_PATH", "/tmp/etl_status.json")
OUT_DIR = os.environ.get("ETL_OUT_DIR", "/tmp")
SHEETS_SYNC_ENABLED = os.environ.get("SHEETS_SYNC_ENABLED", "true").lower() in ("1","true","yes")

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
        s = {"job": name, "status": "ok", "started": started, "ended": datetime.utcnow().isoformat(), "result": result}
    except Exception as e:
        s = {"job": name, "status": "error", "started": started, "ended": datetime.utcnow().isoformat(),
             "error": str(e), "trace": traceback.format_exc()}
    _write_status(s)
    return s

def refresh_orders_inventory_finances(days_back:int=30):
    orders = sp.list_orders(days_back=days_back)
    inv = sp.list_inventory()
    fin = sp.list_finances(days_back=days_back)
    os.makedirs(OUT_DIR, exist_ok=True)
    orders.to_csv(os.path.join(OUT_DIR, "orders.csv"), index=False)
    inv.to_csv(os.path.join(OUT_DIR, "inventory.csv"), index=False)
    fin.to_csv(os.path.join(OUT_DIR, "finances.csv"), index=False)
    res = {}
    if SHEETS_SYNC_ENABLED:
        res["orders_sync"] = write_df("orders", orders)
        res["inventory_sync"] = write_df("inventory", inv)
        res["finances_sync"] = write_df("finances", fin)
    return {"orders": len(orders), "inventory": len(inv), "finances": len(fin), **res}

def monthly_profitability_rollup():
    fin_path = os.path.join(OUT_DIR, "finances.csv")
    if not os.path.exists(fin_path):
        df = pd.DataFrame(columns=["date","sku","asin","revenue","fees","other"])
    else:
        df = pd.read_csv(fin_path)
    if df.empty or "date" not in df.columns:
        roll = pd.DataFrame(columns=["month","sku","revenue","fees","other"])
    else:
        df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").astype(str)
        roll = df.groupby(["month","sku"], as_index=False).agg(revenue=("revenue","sum"), fees=("fees","sum"), other=("other","sum"))
    os.makedirs(OUT_DIR, exist_ok=True)
    roll.to_csv(os.path.join(OUT_DIR, "profitability_monthly.csv"), index=False)
    res = {}
    if SHEETS_SYNC_ENABLED:
        res["profitability_monthly_sync"] = write_df("profitability_monthly", roll)
    return {"rows": len(roll), **res}

if __name__ == "__main__":
    print(run_job("refresh_orders_inventory_finances", refresh_orders_inventory_finances))
    print(run_job("monthly_profitability_rollup", monthly_profitability_rollup))
