from vega.infra.sheets_client import SheetsClient
from datetime import datetime

def load_daily_kpis():
    sc = SheetsClient()
    return sc.read_table("KPIs_Daily")

def record_error(source: str, context: str, message: str, stack: str = ""):
    sc = SheetsClient()
    rows = [{
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "context": context,
        "message": message,
        "stack": stack
    }]
    sc.upsert_rows("Errors_Log", keys=["timestamp","source"], rows=rows)