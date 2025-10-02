from vega.infra.sheets_client import SheetsClient
from datetime import datetime
from typing import List, Dict, Any

def list_alerts() -> List[Dict[str, Any]]:
    sc = SheetsClient()
    return sc.read_table("Alerts")

def add_alert(severity: str, component: str, message: str):
    sc = SheetsClient()
    rows = [{
        "date": datetime.utcnow().date().isoformat(),
        "severity": severity,
        "component": component,
        "message": message,
        "resolved": "",
        "resolved_at": ""
    }]
    sc.upsert_rows("Alerts", keys=["date","component","message"], rows=rows)

def resolve_alert(component: str, message: str):
    sc = SheetsClient()
    rows = [{
        "date": datetime.utcnow().date().isoformat(),
        "severity": "",
        "component": component,
        "message": message,
        "resolved": "TRUE",
        "resolved_at": datetime.utcnow().isoformat()
    }]
    sc.upsert_rows("Alerts", keys=["date","component","message"], rows=rows)